# subset-b-008564 Research

Grouped research report for RocksDB HyperClock cache and compressed secondary cache sources. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/clock_cache.cc -->
# sources/storage-engines/rocksdb/cache/clock_cache.cc

## Purpose
Implements RocksDB's HyperClock cache variants, the CLOCK-style alternatives to the block-cache LRU. The file supplies the algorithms declared in `clock_cache.h`: fixed-size open-addressed `FixedHyperClockTable`, dynamically growing linear-hash `AutoHyperClockTable`, shard-level cache operations, diagnostics, and public construction through `HyperClockCacheOptions::MakeSharedCache`. The deprecated `NewClockCache` factory intentionally returns an LRU cache for compatibility rather than this implementation.

## Important APIs, Types, And Functions
The central entry points are `BaseClockTable::Insert`, `FixedHyperClockTable::{DoInsert,Lookup,Release,Erase,Evict}`, `AutoHyperClockTable::{Grow,SplitForGrow,DoInsert,Lookup,Release,Erase,Evict}`, `ClockCacheShard` methods, `BaseHyperClockCache` accessors, and `HyperClockCacheOptions::MakeSharedCache`.

Important internal helpers include `ClockUpdate`, `CorrectNearOverflow`, `BeginSlotInsert`, `FinishSlotInsert`, `TryInsert`, `Unref`, `FreeDataMarkEmpty`, `ConstApplyToEntriesRange`, `ChainRewriteLock`, `PurgeImpl`, and the linear-hash metadata helpers around `length_info_`. `TrackAndReleaseEvictedEntry` integrates eviction callbacks and reconstructs the original 16-byte cache key from the reversible hash.

## Control Flow
Insertion starts in `ClockCacheShard::Insert`, validates the fixed 16-byte key requirement, builds a `ClockHandleBasicData` prototype, and delegates to `BaseClockTable::Insert`. The base path increments occupancy optimistically, asks the concrete table to grow or admit the new occupancy, charges usage under strict or non-strict capacity rules, evicts if necessary, and calls the table-specific `DoInsert`. If table insertion cannot happen and the caller needs a handle, insertion falls back to a heap-allocated standalone invisible handle and returns `OkOverwritten`; if no handle is needed, the value is freed as if it were immediately evicted.

`FixedHyperClockTable` uses double hashing over a fixed power-of-two slot array. `DoInsert` probes with `FindSlot`, transitions an empty slot through construction to visible, tracks displacement counters for early lookup termination, and rolls displacements back when an existing key or failed insert aborts the path. `Lookup` probes the same sequence, optimistically increments the acquire counter, checks visibility and hash equality, sets the hit bit for eviction callbacks, and undoes non-matching references. `Release` usually increments the release counter or decrements acquire for `useful=false`; when erasing or releasing an invisible last reference, it CASes to construction, frees, rolls back displacements, and reclaims usage.

`AutoHyperClockTable` uses lazy anonymous mmap storage and linear hashing. `GrowIfNeeded` may reserve new slots with `Grow`; `Grow` splits one existing chain into two through `SplitForGrow`, then opportunistically publishes longer `length_info_` and occupancy limits. `DoInsert` first tries the home slot, then a recently opened slot, then bounded linear probing plus large pseudo-random jumps; after owning a slot it links the entry at the chain head while preserving any rewrite-lock bit. `Lookup` first runs a short naive chain traversal for speed, then falls back to a careful wait-free traversal that holds at most one known-good read reference for backtracking across concurrent split, insert, remove, or construction states.

Eviction is driven by insertion. Fixed-table eviction advances a shared clock pointer in batches of four slots and calls `ClockUpdate` directly. Auto-table eviction advances over home chains based on a stable clock mask, uses `PurgeImpl` and chain rewrite locks to clock-update and remove entries from chains, and finishes freeing outside the lock. Both variants stop when requested charge is freed, the clock effort budget is exhausted, or the configured eviction-effort cap indicates too many pinned entries were encountered.

## State And Persistence Behavior
The cache state is in memory only. Durable RocksDB state is not modified. Per-entry state lives in `ClockHandle::meta`, a packed atomic word containing acquire counter, release counter, hit flag, occupied flag, shareable flag, and visible flag. Logical states are empty, under construction, visible shareable, invisible shareable, and standalone invisible. The countdown clock is encoded by equal acquire/release counters when refcount is zero.

Shard/table aggregate state includes `clock_pointer_`, `occupancy_`, `usage_`, `standalone_usage_`, `capacity_`, strict-capacity and eviction-effort bits, and diagnostic counters. Fixed tables additionally keep immutable table size, occupancy limit, and per-slot displacement counters. Auto tables maintain mmap-backed slots, `head_next_with_shift` and `chain_next_with_shift` decorated pointers, `length_info_`, `occupancy_limit_`, `grow_frontier_`, and `clock_pointer_mask_`. Metadata charge policy can include table-slot bytes in `usage_`, and Auto table metadata usage grows as more slots are published.

## Dependencies And Integration Points
Depends on cache primitives in `cache/cache_key.h`, `cache/sharded_cache.h`, `rocksdb/cache.h`, secondary-cache adaptation in `cache/secondary_cache_adapter.h`, reversible hash utilities, `BitFieldsAtomic`, `RelaxedAtomic`, `TypedMemMapping`, logging, random sampling, and RocksDB memory allocation callbacks. `BaseHyperClockCache` plugs into `ShardedCache`, exposing value, charge, helper, per-handle callbacks, shard stats, and `ReportProblems`.

Integration points include block-based table block cache users, secondary cache wrapping through `CacheWithSecondaryAdapter`, eviction callbacks, cache metadata charging, strict capacity mode, `ApplyToSomeEntries`, `EraseUnRefEntries`, cache benchmarks, cache tests, and DB stress configurations that choose fixed versus auto HyperClock based on `estimated_entry_charge`.

## Risks And Edge Cases
The implementation relies on subtle atomic state transitions. `Release` and erase paths acknowledge a small chance that a slot is replaced between last-reference detection and erase, possibly erasing a different entry; the code treats this as acceptable imprecision. Counter overflow correction assumes live references never reach many millions and that paused threads do not outlive many millions of acquire/release cycles on a reused slot. Invisible or duplicate entries may remain until later eviction.

Fixed-table risk centers on table sizing and displacement bookkeeping. Too-small or inaccurate `estimated_entry_charge` can create occupancy pressure, standalone fallback, reduced effective capacity, or high probe cost. Strict-capacity insertions may fail if eviction cannot reclaim enough charge or occupancy; non-strict mode can transiently exceed capacity and pays down later.

Auto-table risk centers on the linear-hash chain protocol. `SplitForGrow`, `PurgeImpl`, and full `Lookup` must preserve visibility during concurrent chain rewrites; the file uses iteration caps and `std::terminate()` as cycle/spin protection. The short naive lookup fast path appears suspicious as written: it selects `&arr[next_with_shift.IsEnd()]` while the loop condition has already established `!IsEnd()`, so it indexes slot 0 rather than `next_with_shift.GetNext()`. The later full lookup can recover misses, but this fast path likely defeats its intended benefit and can read the wrong slot.

Pinned entries are a known pathological case. If many entries are referenced or a large entry dominates a small shard, insertion can spend CPU scanning without freeing enough space. `Release` deliberately does not proactively evict just because the cache is over capacity.

## Test Signals
Direct unit coverage is in `cache/lru_cache_test.cc` under typed `ClockCacheTest` for auto and fixed variants: miscellaneous operation behavior, limits, clock eviction, eviction effort cap, counter overflow, table-full behavior, colliding insert/erase, and table sizes. Broader `cache/cache_test.cc` parametrizes cache behavior across LRU, fixed HyperClock, and auto HyperClock, with special expectations for 16-byte keys, non-guaranteed overwrite, metadata charging, and capacity behavior. `cache_bench_tool.cc` and DB stress configurations provide performance and concurrency signals. Runtime diagnostics are emitted by `ReportProblems`, including slot occupancy variance, eviction effort exceeded, fixed-cache load-factor recommendations, auto-cache head occupancy, entries-at-home counts, and yield counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/clock_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/clock_cache.h -->
# sources/storage-engines/rocksdb/cache/clock_cache.h

## Purpose
Declares the internal structure and public cache classes for RocksDB HyperClock cache. The header is unusually explanatory: it documents the design goal of a mostly lock-free/read-optimized CLOCK cache for block-cache use, contrasts fixed and automatic table sizing, specifies key limitations, and lays out the packed reference-count and slot-state protocol used by the implementation.

## Important APIs, Types, And Functions
`ClockHandleBasicData` is the cache handle payload: object pointer, item helper, reversible 128-bit key hash, and total charge. `ClockHandle` adds the atomic `SlotMeta` word. `SlotMeta` defines acquire/release counters plus hit, occupied, shareable, and visible flags, with convenience methods for empty, construction, visible, and invisible states.

`BaseClockTable` declares shared insertion, standalone-handle creation, capacity and usage accounting, reference acquisition, eviction accounting, and diagnostic counters. `FixedHyperClockTable` declares the fixed open-addressed table, its 64-byte `HandleImpl`, displacement counters, load-factor constants, lookup/insert/release/erase APIs, and occupancy-limit helpers. `AutoHyperClockTable` declares the mmap-backed growing linear-hash table, its decorated `NextWithShift` chain pointers, rewrite-lock-based chain maintenance, growth, purge, lookup, eviction, and table-size APIs.

`ClockCacheShard<TableT>` adapts either table to the `CacheShardBase` concept and supplies hashed-key computation, reverse hashing, insert, standalone creation, lookup, ref/release, erase, usage, pinned usage, occupancy, and scanning APIs. `BaseHyperClockCache<Table>` adapts shards to `ShardedCache`. `FixedHyperClockCache` and `AutoHyperClockCache` provide concrete cache names and diagnostics.

## Control Flow
The header defines the intended lifecycle. Insert reserves occupancy/usage, chooses an empty slot, initializes payload while the slot is under construction, then publishes it as visible with the initial priority countdown encoded into counters. Lookup computes a reversible hash from the 16-byte block-cache key, finds a slot or chain entry, increments the acquire counter, validates visible key equality, and returns a pinned handle. Release either increments the release counter, or for `useful=false` decrements acquire to undo the use signal. Erase marks visible entries invisible or takes construction ownership and frees them if unreferenced.

CLOCK eviction sweeps candidate entries. Unreferenced visible entries with positive countdown are aged by decrementing the counters; unreferenced visible entries with zero countdown and unreferenced invisible entries are transitioned to construction for deletion. Referenced entries are counted as pinned and skipped. Fixed tables sweep direct slots; auto tables sweep chains and purge construction entries under per-chain rewrite locks.

The fixed variant keeps a non-resizable table sized from `capacity`, `estimated_entry_charge`, metadata charge policy, and a target load factor. The auto variant uses linear hashing over a pre-reserved mmap range, starts small, grows incrementally as occupancy rises, and keeps shift-tagged chain links so lookup remains safe while growth splits chains.

## State And Persistence Behavior
All state is in process memory. There is no file or manifest persistence. Handles carry value ownership and call `CacheItemHelper::del_cb` through `FreeData`. The packed atomic `SlotMeta` is the core consistency state: empty slots have no defined payload, construction slots are exclusively owned, visible slots can be found by lookup, invisible slots preserve existing references but hide from lookup, and standalone handles are heap-allocated invisible entries outside table occupancy.

Usage accounting distinguishes table-tracked `usage_`, `standalone_usage_`, occupancy, capacity, strict-capacity mode, and metadata charge policy. Auto-table persistence-like behavior is limited to the lifetime of an anonymous memory mapping; growing only maps/uses more of the reserved address space and may increase metadata charge.

## Dependencies And Integration Points
The header depends on `cache/cache_key.h`, `cache/sharded_cache.h`, `rocksdb/cache.h`, `port/mmap.h`, `util/atomic.h`, `util/bit_fields.h`, and math utilities. It is compiled into the RocksDB cache subsystem and connected to users through `HyperClockCacheOptions`, `ShardedCache`, `CacheWithSecondaryAdapter`, block-cache helpers, memory allocators, cache eviction callbacks, and tests that friend `clock_cache::ClockCacheTest`.

The fixed and auto classes share one shard/cache adapter layer, so public cache behavior is mostly uniform while table organization differs. Key hashing is deliberately lossless for 16-byte block-cache keys, allowing eviction callbacks and `ApplyToHandle` to reconstruct the original key from `UniqueId64x2`.

## Risks And Edge Cases
The documented limitations are material: HyperClock cache supports only exact 16-byte keys, does not guarantee insert overwrite for an existing key, enforces priorities less aggressively than LRU, and may free erased or duplicate entries only on later eviction. High shard counts, small capacities, large entries, and many pinned entries can make eviction expensive or ineffective. Internal counters can overflow if simultaneous references are extremely high.

Fixed HyperClock has a sizing risk because the table does not resize; an inaccurate estimated entry charge can waste memory, hit occupancy limits before capacity, or force standalone handles. Auto HyperClock removes that fixed sizing issue but introduces localized waits for chain rewrite locks during growth/removal and depends on careful shift-tagged chain invariants.

## Test Signals
The header's friend hooks and `TEST_` methods are used by `cache/lru_cache_test.cc` typed `ClockCacheTest` cases. Observable signals include `GetUsage`, `GetStandaloneUsage`, `GetOccupancy`, `GetOccupancyLimit`, `GetTableSize`, pinned usage scans, yield counts, eviction-effort-exceeded counts, and diagnostic logging from the concrete cache classes. General cache API tests in `cache/cache_test.cc` must account for HyperClock-specific behavior, especially 16-byte keys and weak overwrite semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/clock_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/compressed_secondary_cache.cc -->
# sources/storage-engines/rocksdb/cache/compressed_secondary_cache.cc

## Purpose
Implements `CompressedSecondaryCache`, a concrete `SecondaryCache` backed by an internal LRU cache that stores serialized block payloads, optionally compressed, with a small tag identifying source tier and compression type. It supports RocksDB's secondary-cache adapter by acting as a compressed off-primary block cache and using dummy placeholder entries to coordinate promotion/admission decisions between primary and secondary cache.

## Important APIs, Types, And Functions
Primary entry points are `CompressedSecondaryCache::Lookup`, `Insert`, `InsertSaved`, `Erase`, `SetCapacity`, `GetCapacity`, `Deflate`, `Inflate`, and `GetPrintableOptions`. Internal helpers are `MaybeInsertDummy`, `InsertInternal`, `SplitValueIntoChunks`, `MergeChunksIntoValue`, `GetHelper`, and `TEST_GetCharge`. The anonymous helpers define the stored value format and compute `GetHeaderSize`.

The on-cache value is either a length-prefixed tagged byte sequence or, when custom split/merge is enabled, a linked list of `CacheValueChunk` objects. The first two bytes of the tagged data encode `CacheTier source` and `CompressionType type`; payload bytes are the saved block representation or compressed saved data.

## Control Flow
Construction creates an internal LRU cache from `CompressedSecondaryCacheOptions`, builds a cache reservation manager, sets `disable_cache_` when capacity is zero, and acquires compressor/decompressor objects from the builtin V2 compression manager.

`Lookup` returns null immediately when disabled or when the internal LRU has no entry. If the found value is null, it is a dummy hit: the function releases it, records `COMPRESSED_SECONDARY_CACHE_DUMMY_HITS`, and returns null. For a real value, lookup reconstructs tagged bytes from chunks or a length-prefixed allocation, reads source and compression type, and if this cache compressed the value (`kVolatileCompressedTier`) it decompresses to an uncompressed saved slice and rewrites the source to `kVolatileTier`. It then calls the caller's `create_cb` to materialize a cache object. If `advise_erase` is true, it erases the real secondary value on release and immediately inserts a zero-charge dummy; otherwise it leaves the secondary value in place and sets `kept_in_sec_cache`.

`Insert` rejects null values. Unless forced, it calls `MaybeInsertDummy`; when no secondary entry exists yet, that function inserts a null dummy and `Insert` returns without storing real data. If a dummy or real entry already exists, `InsertInternal` serializes the object through `helper->saveto_cb`, optionally compresses if the source object is uncompressed and the role is not excluded, writes the two-byte tag, and inserts into the internal LRU either as chunks or as a length-prefixed allocation.

`InsertSaved` handles values already saved by an upstream tier. It rejects `kVolatileCompressedTier`, no-compression saved slices, and custom split/merge mode, then applies the same dummy admission check before storing through `InsertInternal` using the slice helper. Capacity changes are mutex-protected, update options and the internal cache capacity, and flip `disable_cache_`.

## State And Persistence Behavior
All data is volatile memory in the internal LRU cache. There is no disk persistence. Entries can be real tagged byte payloads or null dummy placeholders. Dummies are used as a state protocol: first primary-cache eviction inserts a zero-charge dummy in secondary; a later eviction with the same key can replace it with real data, while lookup with `advise_erase` can remove real data and restore a dummy.

Usage and charge are tracked by the internal cache. Non-split values charge either `malloc_usable_size` when available or tagged payload size. Split values charge the allocated chunk sizes, not just payload bytes, to reflect malloc bins. `Deflate` and `Inflate` update a `ConcurrentCacheReservationManager`, enabling integration with memory reservation systems. `disable_cache_` is a relaxed atomic boolean derived from capacity zero.

## Dependencies And Integration Points
Depends on `cache/cache_reservation_manager.h`, `memory/memory_allocator_impl.h`, `rocksdb/advanced_compression.h`, `rocksdb/secondary_cache.h`, `util/coding.h`, `util/compression.h`, `util/string_util.h`, perf context counters, LRU cache options inherited by `CompressedSecondaryCacheOptions`, and `Cache::CacheItemHelper` callbacks.

It integrates with `CacheWithSecondaryAdapter`, block cache item helpers, tiered secondary-cache tests, blob secondary-cache paths, DB stress options, and statistics/perf counters such as compressed bytes, uncompressed bytes, real insert count, dummy insert count, cache hits, and dummy hits.

## Risks And Edge Cases
`Lookup` assumes in-memory compressed data should decompress successfully and asserts before returning null on failure. Malformed tag bytes or mismatched helper behavior can produce wrong source/type creation calls. `InsertInternal` preallocates for original bytes before possible compression, so large values can temporarily require multiple copies; the code explicitly clears `merged_value` after decompression to reduce peak copies.

The dummy protocol is subtle: an initial non-forced insert often stores only a placeholder rather than data, which is intentional for admission but can look like a missed insert. `InsertSaved` silently returns OK for unsupported combinations, including no-compression saved data and custom split/merge, so callers must understand that OK does not always mean a real entry was stored. Custom split/merge currently uses raw `new char[]`, ignores the configured allocator, and has FIXME notes about fragmentation and overhead.

## Test Signals
Direct coverage is concentrated in `cache/tiered_secondary_cache_test.cc`, which exercises compressed secondary cache admission, lookup, dummy behavior, usage/charge, advise-erase, forced insertion, and split/merge-like capacity outcomes. Blob-cache integration is covered by `db/blob/blob_source_test.cc`, `db/blob/db_blob_basic_test.cc`, and direct-write blob tests. DB stress uses compressed secondary cache flags and can combine it with HyperClock or LRU primary caches. Runtime signals include `TEST_GetUsage`, `TEST_GetCharge`, statistics ticks, and perf counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/compressed_secondary_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/compressed_secondary_cache.h -->
# sources/storage-engines/rocksdb/cache/compressed_secondary_cache.h

## Purpose
Declares RocksDB's compressed secondary cache implementation and its synchronous result handle. The class implements `rocksdb::SecondaryCache` with an internal cache that stores compressed or saved block data and supports the dummy-placeholder protocol described in the header comments.

## Important APIs, Types, And Functions
`CompressedSecondaryCacheResultHandle` implements `SecondaryCacheResultHandle` for synchronous lookups: `IsReady` is always true, `Wait` is a no-op, `Value` returns the materialized cache object, and `Size` returns its charge.

`CompressedSecondaryCache` overrides `SecondaryCache::{Insert,InsertSaved,Lookup,Erase,WaitAll,SetCapacity,GetCapacity,Deflate,Inflate,GetPrintableOptions}` and reports `Name()` as `"CompressedSecondaryCache"`. It exposes `SupportForceErase`, `TEST_GetUsage`, and private test access through `CompressedSecondaryCacheTestBase`.

Important private members include the internal `std::shared_ptr<Cache> cache_`, copied `CompressedSecondaryCacheOptions`, `Compressor`, `Decompressor`, `capacity_mutex_`, `ConcurrentCacheReservationManager`, and relaxed `disable_cache_`. `CacheValueChunk` and `malloc_bin_sizes_` support optional chunking to reduce allocator-bin waste.

## Control Flow
The declared API supports two data paths. `Insert` receives a live cache object plus helper callbacks, possibly inserts or observes a dummy, serializes the object, compresses when allowed, and stores tagged bytes in the internal cache. `InsertSaved` receives an already serialized payload and preserves the upstream compression type/source where supported. `Lookup` retrieves a real tagged payload, optionally decompresses it, calls the provided helper to recreate the object, optionally erases from secondary, and returns a synchronous result handle.

The header comments define the dummy control protocol. On lookup, if a dummy block with the key exists in primary, the secondary value is erased and promoted into primary; otherwise a primary dummy is inserted and a standalone handle is returned. On primary eviction, the secondary cache either replaces an existing dummy with real compressed data or inserts a secondary dummy of size zero.

## State And Persistence Behavior
State is volatile and scoped to the process. The internal cache stores either null dummy entries or allocated serialized byte/chunk payloads. `CacheValueChunk` owns linked chunk allocations and frees them through its helper. Capacity is mutable under `capacity_mutex_`, and capacity zero disables lookup/insert behavior through `disable_cache_`. The cache reservation manager lets external memory-pressure code deflate or inflate the cache's reservation.

## Dependencies And Integration Points
Depends on RocksDB cache reservation management, memory allocator support, advanced compression manager APIs, `rocksdb::SecondaryCache`, `rocksdb::Slice`, `rocksdb::Status`, and atomic utilities. The options object supplies LRU cache settings, compression type/options, allocator, excluded roles, capacity, and custom split/merge mode. The implementation is used through `NewCompressedSecondaryCache`/`CompressedSecondaryCacheOptions::MakeSharedSecondaryCache` and by primary-cache secondary adapters.

## Risks And Edge Cases
The class is synchronous despite using the secondary-cache result-handle abstraction; callers waiting for async behavior will observe immediate readiness. The dummy protocol means presence of a key can represent admission state rather than cached bytes. Split/merge mode owns chunks through raw linked allocations and is explicitly marked for cleanup in the implementation. `InsertSaved` support is narrower than the interface suggests: some source/type/mode combinations are accepted as OK but not stored as real data.

## Test Signals
Header-level behavior is validated through implementation tests in `cache/tiered_secondary_cache_test.cc`, blob secondary-cache tests, and stress-tool configurations. Useful observable signals are `SupportForceErase`, `TEST_GetUsage`, result-handle readiness/value/size, capacity get/set results, and the behavior of dummy hits versus real hits in statistics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/compressed_secondary_cache.h -->

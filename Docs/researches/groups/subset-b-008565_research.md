# Research: subset-b-008565

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/compressed_secondary_cache_test.cc -->
# sources/storage-engines/rocksdb/cache/compressed_secondary_cache_test.cc

## Purpose
This GoogleTest file validates RocksDB's compressed secondary cache and its tiered-cache integration with primary caches. It exercises direct `SecondaryCache` behavior, integration through `CacheWithSecondaryAdapter`, custom split/merge value storage, cache-entry role compression policy, and dynamic capacity/reservation behavior in `NewTieredCache`.

## Important APIs, Types, And Functions
`CompressedSecondaryCacheTestBase` provides reusable helpers for several parameterized suites. `BasicTestHelper()` verifies direct compressed-secondary-cache insert/lookup semantics, including dummy-entry admission on first insert and real insertion on later eviction. `BasicIntegrationTest()` builds a primary cache with a compressed secondary cache and checks demotion, promotion, dummy primary entries, capacity changes, and `PerfContext` counters. `FailsTest()`, `BasicIntegrationFailTest()`, `IntegrationSaveFailTest()`, `IntegrationCreateFailTest()`, and `IntegrationFullCapacityTest()` cover failed object creation, failed serialization, missing helpers, and promotion under full primary capacity. `SplitValueIntoChunksTest()`, `MergeChunksIntoValueTest()`, and `SplictValueAndMergeChunksTest()` directly validate `CompressedSecondaryCache::CacheValueChunk` split/merge helpers. `CompressedSecCacheTestWithTiered` exercises `NewTieredCache()`, `CacheReservationManager`, `UpdateTieredCache()`, and admission policy behavior for LRU and HyperClock primary caches.

## Control Flow
The direct-cache tests first insert a dummy entry, confirm lookup miss, then insert the same key again to materialize compressed or uncompressed payload storage. Lookups with `advise_erase=true` are expected to remove the secondary entry, while lookups without erase can keep it. Integration tests drive a small strict-capacity primary cache so inserts evict older entries into the secondary cache; later lookups promote secondary results back through `CacheWithSecondaryAdapter`, sometimes as standalone handles plus dummy markers. Tiered tests construct a combined primary/secondary budget and then mutate reservations, total capacity, and compressed-secondary ratio to ensure usage moves between tiers in chunked increments.

## State And Persistence Behavior
The tests observe secondary-cache state through `TEST_GetCharge()`, `TEST_GetUsage()`, `GetCapacity()`, perf counters, and returned result handles. They do not persist data to disk; persistence is in-memory cache state. Important state transitions include dummy-to-real secondary entries, compressed-byte accounting, kept-versus-erased secondary handles, split chunk ownership through helper deleters, and tiered reservation accounting across primary placeholder entries and compressed secondary capacity.

## Dependencies And Integration Points
The file depends on `cache/compressed_secondary_cache.h`, `cache/secondary_cache_adapter.h`, `rocksdb/cache.h`, `rocksdb/convenience.h`, `test_util/secondary_cache_test_util.h`, `JemallocNodumpAllocator`, `PerfContext`, and RocksDB cache option factories. It is parameterized across cache types from `secondary_cache_test_util::GetTestingCacheTypes()` and across compression enabled/disabled cases. LZ4 availability gates compressed tests. Tiered tests integrate `PrimaryCacheType`, `TieredAdmissionPolicy`, LRU/HyperClock options, and `CacheReservationManagerImpl`.

## Risks And Edge Cases
The most important risks covered are silent loss on failed serialization or failed create callbacks, stale secondary entries after promotion, incorrect dummy-handle handling, compressed-size accounting regressions, allocator-specific chunk deallocation, and reservation drift after dynamic tiered-cache updates. Some assertions tolerate HCC differences, so behavior is not perfectly uniform across primary cache implementations. Tests also depend on exact perf counter increments and small capacities, which can be sensitive to metadata charge or cache policy changes.

## Test Signals
This file is itself a test suite. Strong signals include `ASSERT_OK`/`ASSERT_NOK` around secondary inserts, data equality after `SecondaryCacheResultHandle::Value()`, perf-context counters such as `compressed_sec_cache_insert_dummy_count`, `compressed_sec_cache_insert_real_count`, `compressed_sec_cache_uncompressed_bytes`, `compressed_sec_cache_compressed_bytes`, and `block_cache_standalone_handle_count`, plus tiered usage checks with `CacheUsageWithinBounds()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/compressed_secondary_cache_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/lru_cache.cc -->
# sources/storage-engines/rocksdb/cache/lru_cache.cc

## Purpose
This file implements RocksDB's sharded LRU cache shard, handle hash table, and `LRUCacheOptions` factories. It is the concrete implementation behind `NewLRUCache()`/`LRUCacheOptions::MakeSharedCache()` and can optionally be wrapped by `CacheWithSecondaryAdapter` when a secondary cache is configured.

## Important APIs, Types, And Functions
`LRUHandleTable` implements a compact bucketed hash table with `Lookup()`, `Insert()`, `Remove()`, `FindPointer()`, and `Resize()`, indexing by upper hash bits because lower bits are used for sharding. `LRUCacheShard` implements capacity changes, insertion, lookup, ref/release, erase, LRU-list maintenance, priority pools, standalone handle creation, usage queries, and iteration. `LRUCache` adapts shard internals to the public `Cache` API and exposes handle value/charge/helper access. `LRUCacheOptions::MakeSharedCache()` validates option ratios, picks default shard bits, constructs `LRUCache`, and wraps it with `CacheWithSecondaryAdapter` when `secondary_cache` is set.

## Control Flow
Insertion allocates an `LRUHandle`, sets priority and in-cache flags, evicts LRU entries until there is room, and inserts the handle into the hash table. If the caller does not request a handle, the entry is placed on the LRU list immediately; otherwise it is pinned by an external ref. Lookup removes an unreferenced cache entry from the LRU list, increments `refs`, and marks it hit. Release decrements refs; the last referenced in-cache entry either returns to the priority-partitioned LRU list, is erased when over capacity or requested, or is freed if no longer in cache. Erase removes from the table and frees immediately only when there are no external refs. Capacity and pool-ratio changes trigger eviction or pool rebalancing under the shard mutex.

## State And Persistence Behavior
State is in-memory only. `usage_` tracks charged cache bytes, `lru_usage_` tracks bytes currently evictable on the LRU list, and pinned usage is `usage_ - lru_usage_`. `high_pri_pool_usage_` and `low_pri_pool_usage_` track priority-reserved portions. Each `LRUHandle` carries value, helper, hash, key bytes, total charge, refs, mutable cache/list flags, and immutable priority/standalone flags. There is no disk persistence, but eviction callbacks can transfer ownership to secondary-cache adapters.

## Dependencies And Integration Points
The implementation depends on `cache/sharded_cache.h`, `cache/secondary_cache_adapter.h`, `monitoring/perf_context_imp.h`, `monitoring/statistics_impl.h`, `util/distributed_mutex.h`, allocator metadata helpers, and RocksDB `Cache` helper callbacks. `LRUCacheShard` is a template parameter to `ShardedCache<LRUCacheShard>`. Eviction callbacks are installed by the cache wrapper and are the handoff point for secondary-cache demotion.

## Risks And Edge Cases
The code has tight invariants around `refs`, `M_IN_CACHE`, list membership, and usage accounting. Incorrect pool pointer updates can corrupt priority pools, especially when capacity shrinks and entries overflow from high to low to bottom priority pools. Strict capacity behavior differs depending on whether the caller requested a handle. `CreateStandalone()` can return uncharged handles when strict capacity would otherwise reject them, so callers must treat standalone handles differently from cache-resident entries. Eviction callback ownership is subtle: if it takes ownership, the handle is freed without calling the normal value deleter.

## Test Signals
`lru_cache_test.cc` directly validates LRU ordering, high/low/bottom priority pool behavior, capacity reduction, and insertion after shrinking capacity. Secondary-cache tests validate the factory path where `LRUCacheOptions::MakeSharedCache()` wraps LRU in `CacheWithSecondaryAdapter`. Compressed-secondary tests also exercise eviction callbacks through primary-cache demotion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/lru_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/lru_cache.h -->
# sources/storage-engines/rocksdb/cache/lru_cache.h

## Purpose
This header declares the internal LRU cache structures used by RocksDB's sharded cache framework. It defines the handle state machine, custom hash table, per-shard cache API, and the `LRUCache` public wrapper class.

## Important APIs, Types, And Functions
`LRUHandle` extends `Cache::Handle` and stores object pointer, helper, hash-chain link, LRU-list links, charge, key, hash, refs, and flags. It provides `Ref()`, `Unref()`, `HasRefs()`, cache/pool/priority predicates, flag setters, `Free()`, metadata-charge calculation, and charge access. `LRUHandleTable` declares lookup/insert/remove and ranged iteration. `LRUCacheShard` declares the shard operations expected by `ShardedCache`: `ComputeHash()`, `Insert()`, `CreateStandalone()`, `Lookup()`, `Release()`, `Ref()`, `Erase()`, capacity and strict-limit setters, usage/occupancy queries, partial iteration, and `EraseUnRefEntries()`. `LRUCache` derives from `ShardedCache<LRUCacheShard>` and exposes public `Cache` overrides.

## Control Flow
The header documents three handle states: externally referenced and in cache; unreferenced and in cache/LRU; externally referenced and detached from cache. Public methods move handles among these states: lookup moves unreferenced cache entries out of LRU and increments refs, release may return entries to LRU or free them, erase/overwriting detaches entries from the hash table, and insert may evict older LRU entries before installing a new one.

## State And Persistence Behavior
The declared state is volatile cache metadata. `LRUCacheShard` owns capacity, high/low pool ratios and cached pool capacities, a circular dummy LRU head, boundary pointers for low and bottom priority pools, `LRUHandleTable`, usage counters, a `DMutex`, and an eviction callback reference. The header explicitly separates frequently and infrequently modified fields to reduce false sharing.

## Dependencies And Integration Points
The header depends on `cache/sharded_cache.h`, port alignment/malloc helpers, `util/autovector.h`, and `util/distributed_mutex.h`. It is consumed by `lru_cache.cc`, tests, and factory code. Type aliases expose `LRUCache`, `LRUHandle`, and `LRUCacheShard` in `ROCKSDB_NAMESPACE` for callers and tests.

## Risks And Edge Cases
The main risk is violating handle/list invariants: `key_data` must remain the last field, `Free()` requires `refs == 0` and a valid helper, and metadata-charge calculation depends on allocator support. The mutable/immutable flag split relies on callers only changing immutable flags during single-threaded setup. The shard API is not independently thread-safe unless operations use its mutex as implemented in the `.cc`.

## Test Signals
Tests access `TEST_GetLRUList()`, `TEST_GetLRUSize()`, and priority predicates on `LRUHandle` to assert exact list order and pool membership. Secondary-cache tests indirectly validate that public aliases and `LRUCacheOptions` produce usable cache instances compatible with block-cache helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/lru_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/lru_cache_test.cc -->
# sources/storage-engines/rocksdb/cache/lru_cache_test.cc

## Purpose
This GoogleTest file validates LRU cache behavior, clock-cache behavior colocated in the same test file, secondary-cache integration, DB/block-cache integration, cache dump/load into secondary cache, and DB options that enable or bypass secondary cache tiers.

## Important APIs, Types, And Functions
`LRUCacheTest` manually constructs one `LRUCacheShard` and provides helpers for insert, lookup, erase, and exact LRU-list validation. Its tests cover basic LRU order, low-priority midpoint insertion, bottom-priority behavior, priority-pool overflow, and insertion after capacity reduction. The `clock_cache` namespace defines templated `ClockCacheTest` tests for `AutoHyperClockCache` and `FixedHyperClockCache`, including limits, eviction, counter overflow, collisions, and table sizing. `TestSecondaryCache` is a fake `SecondaryCache` backed by an LRU typed cache and supports success, immediate failure, deferred success, and deferred failure. `BasicSecondaryCacheTest` and `DBSecondaryCacheTest` use `NewCache()` with a secondary cache to validate primary/secondary behavior in direct cache and real DB paths. `CacheWithStats` wraps a cache to count inserts and lookups for dump/load tests.

## Control Flow
The LRU unit tests construct a shard, insert keys with different priorities, perform lookups that temporarily pin entries and then release them, and assert precise LRU-list partitioning after each transition. Secondary-cache tests force primary-cache eviction by using small capacities, then verify lookup promotion from `TestSecondaryCache` and demotion on later evictions. DB tests create SST files with known block sizes so data-block cache misses, promotions, and evictions can be observed through secondary-cache insert/lookup counters. Dump/load tests populate a block cache, dump entries through `CacheDumper`, restore them into a secondary cache, reopen a DB, and confirm reads are served through secondary-cache lookups.

## State And Persistence Behavior
Most tests use in-memory cache state, but DB tests create actual RocksDB test databases and SST files. `TestSecondaryCache` serializes values by prefixing a size and storing bytes in an internal LRU cache. It tracks `num_inserts_`, `num_lookups_`, failure injection, saved insertion behavior, a common cache-key prefix, and per-key result modes. The dump/load tests persist cache dumps to files under the test DB path and reload them into secondary cache, validating cache-warm persistence behavior rather than database correctness alone.

## Dependencies And Integration Points
The file depends on LRU and clock cache internals, `cache_helpers.h`, typed cache helpers, DB test utilities, block-based table options, cache dump/load utilities, fault-injection file systems, sync points, and secondary-cache test utilities. It integrates cache APIs with RocksDB block cache, paranoid file checks, compaction, `MultiGet`, `lowest_used_cache_tier`, and unique cache keys.

## Risks And Edge Cases
The tests document several tricky behaviors: LRU-specific over-capacity release behavior differs from HyperClock, secondary-cache insertion errors are intentionally ignored on demotion, promotion can return standalone handles if primary insertion fails, disabled secondary cache must not perform lookup or insertion, shared caches across DBs must respect per-DB cache-tier options, and async `WaitAll()` must process deferred successes and failures without corrupting results. Exact block-count assertions can be sensitive to table-format changes, metadata accounting, or cache-key generation.

## Test Signals
The file is a major behavioral test signal. It asserts exact list order/pool counts, exact secondary insert/lookup counts, per-role secondary hit tickers, `PerfContext::secondary_cache_hit_count`, DB read correctness after cache misses/promotions, no-I/O validation after dump/load with a fault-injection file system, and async lookup results after `WaitAll()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/lru_cache_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/secondary_cache.cc -->
# sources/storage-engines/rocksdb/cache/secondary_cache.cc

## Purpose
This source file anchors the `rocksdb/secondary_cache.h` API in the build. It includes the public secondary-cache interface and cache-entry role definitions but currently has no out-of-line implementation beyond opening and closing the RocksDB namespace.

## Important APIs, Types, And Functions
No functions or types are defined in this file. The meaningful declarations live in `rocksdb/secondary_cache.h`, and role definitions are included from `cache/cache_entry_roles.h`.

## Control Flow
There is no runtime control flow in this translation unit.

## State And Persistence Behavior
There is no state or persistence behavior in this file.

## Dependencies And Integration Points
The file integrates the public secondary-cache header into the library build and ensures the namespace translation unit exists for the secondary-cache module.

## Risks And Edge Cases
Because the file is intentionally empty, the main risk is assuming it implements behavior that actually lives in concrete secondary-cache implementations such as compressed or tiered secondary caches. Any linker-visible behavior must come from headers or other `.cc` files.

## Test Signals
There are no direct tests for this file. Its interfaces are heavily exercised through `lru_cache_test.cc`, `compressed_secondary_cache_test.cc`, `secondary_cache_adapter.cc`, and concrete secondary-cache implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/secondary_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/secondary_cache_adapter.cc -->
# sources/storage-engines/rocksdb/cache/secondary_cache_adapter.cc

## Purpose
This file implements `CacheWithSecondaryAdapter`, the wrapper that combines a primary RocksDB `Cache` with a `SecondaryCache`, plus factory/update helpers for tiered primary plus compressed-secondary caches. It is the main integration point for eviction demotion, secondary lookup promotion, async lookup chaining, admission policy, and distributed reservation accounting.

## Important APIs, Types, And Functions
The constructor installs a primary-cache eviction callback and optionally initializes reservation accounting for tiered compressed-secondary caches. `EvictionHandler()` spills compatible evicted objects to the secondary cache according to `TieredAdmissionPolicy`. `Insert()` forwards to the target cache, handles placeholder reservation redistribution, and warms the secondary cache with compressed saved values for three-queue policy. `Lookup()` checks the primary cache, processes dummy entries, then synchronously queries the secondary cache and calls `Promote()`. `Promote()` records secondary-hit stats and inserts the result into primary cache or returns a standalone handle with a dummy marker. `StartAsyncLookup()`, `StartAsyncLookupOnMySecondary()`, and `WaitAll()` chain asynchronous lookups through inner and outer secondary caches. `SetCapacity()`, `GetSecondaryCacheCapacity()`, `GetSecondaryCachePinnedUsage()`, `UpdateCacheReservationRatio()`, and `UpdateAdmissionPolicy()` manage dynamic tiered-cache settings. `NewTieredCache()` and `UpdateTieredCache()` are public factory/update helpers.

## Control Flow
On eviction, the primary cache calls `EvictionHandler()`, which checks helper compatibility and admission policy before calling `secondary_cache_->Insert()`. On lookup, the adapter first delegates to the primary cache; if it finds a dummy entry, it releases and optionally erases it. A secondary hit is promoted: if the secondary supports force erase and no dummy marker was found, the adapter returns a standalone handle and inserts a dummy marker; otherwise it tries a normal primary insert and falls back to standalone if primary insertion fails. Async lookup first starts through the target cache and only starts the adapter's own secondary lookup when no inner pending lookup or result exists; `WaitAll()` waits inner caches first, then starts/waits the outer secondary tier for remaining misses.

## State And Persistence Behavior
Persistent state is external to this file; adapter state is in-memory wrapper state. It owns `secondary_cache_`, current admission policy, whether cache reservations are distributed, a primary `ConcurrentCacheReservationManager`, `sec_cache_res_ratio_`, and counters for placeholder usage, reserved usage, and secondary-reserved bytes. Reservation changes happen in 1 MiB chunks. `kDummyObj` is a sentinel object used to record recent secondary access without holding the full object in primary cache.

## Dependencies And Integration Points
The implementation depends on `cache/tiered_secondary_cache.h`, stats/perf counters, sync points, cast utilities, `LRUCacheOptions`, `HyperClockCacheOptions`, `NewCompressedSecondaryCache()`, and public `Cache`/`SecondaryCache` helper contracts. It is invoked from `LRUCacheOptions::MakeSharedCache()` when `secondary_cache` is set and from `NewTieredCache()` for combined primary/compressed/nvm tiering.

## Risks And Edge Cases
Ownership and lifetime are subtle: the destructor must clear the target eviction callback to avoid use-after-free; `Promote()` must not double-free objects when primary insertion fails or when a secondary cache keeps its copy; dummy entries must never be exposed through `Value()`. Reservation redistribution relies on assertions that secondary `Deflate()`, `Inflate()`, and reservation updates succeed. Stacked secondary caches have a documented false synchronization point in `WaitAll()`. Admission policy validation must reject incompatible NVM/compressed combinations.

## Test Signals
`lru_cache_test.cc` validates synchronous and async promotion, stats by cache-entry role, failure modes, full-capacity standalone promotion, DB integration, `MultiGet`, dump/load, and per-DB tier disabling. `compressed_secondary_cache_test.cc` validates compressed/tiered reservation distribution, admission policies, dynamic capacity/ratio updates, and `NewTieredCache()` behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/secondary_cache_adapter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/secondary_cache_adapter.h -->
# sources/storage-engines/rocksdb/cache/secondary_cache_adapter.h

## Purpose
This header declares `CacheWithSecondaryAdapter`, a `CacheWrapper` that adds a secondary-cache tier to an existing primary cache. It exposes the public cache methods that need secondary behavior and the tiered-cache reservation/admission update hooks.

## Important APIs, Types, And Functions
The constructor accepts a target cache, a secondary cache, an admission policy, and a `distribute_cache_res` flag. Overridden cache methods include `Insert()`, `Lookup()`, `Release()`, `Value()`, `StartAsyncLookup()`, `WaitAll()`, `GetPrintableOptions()`, `Name()`, `SetCapacity()`, `GetSecondaryCacheCapacity()`, and `GetSecondaryCachePinnedUsage()`. Public update methods are `UpdateCacheReservationRatio()` and `UpdateAdmissionPolicy()`. Test accessors expose the wrapped primary and secondary caches. Private helpers declare eviction handling, secondary async lookup, promotion, dummy-result processing, object cleanup, and reservation state.

## Control Flow
The header establishes the adapter as the layer through which all primary cache operations pass when secondary caching is configured. Inserts and lookups are intercepted to manage secondary warming/promotion, while releases are intercepted to update placeholder reservation accounting when reservation distribution is enabled.

## State And Persistence Behavior
The declared state includes the secondary cache pointer, admission policy, reservation-distribution flag, primary reservation manager, secondary reservation ratio, a mutex dedicated to reservation accounting, and usage counters for placeholders and secondary-reserved bytes. All state is volatile; any durable behavior is delegated to the concrete `SecondaryCache`.

## Dependencies And Integration Points
The header depends on `cache/cache_reservation_manager.h` and `rocksdb/secondary_cache.h`. It is included by `lru_cache.cc`, compressed-secondary tests, and tiered-cache factory code. `CacheWithSecondaryAdapter` is used by `LRUCacheOptions::MakeSharedCache()` and `NewTieredCache()`.

## Risks And Edge Cases
The class stores an eviction callback into the target cache, so destruction order must be handled carefully. Reservation methods use a dedicated mutex to avoid deadlocks with cache operations. The dummy-object path means callers of `Value()` must never receive dummy handles; `ProcessDummyResult()` and `Promote()` enforce that in the implementation.

## Test Signals
Tests cover the public methods through `NewCache(..., secondary_cache)`, `NewTieredCache()`, async lookup APIs, capacity updates, and secondary capacity/pinned usage accessors. Test accessors are used in compressed-tiered tests to inspect underlying cache and secondary-cache usage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/secondary_cache_adapter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/sharded_cache.cc -->
# sources/storage-engines/rocksdb/cache/sharded_cache.cc

## Purpose
This file implements the non-template portions of RocksDB's sharded cache base. It handles hash-seed selection, capacity and strict-limit configuration storage, shard-count helpers, printable options, and default shard-bit selection.

## Important APIs, Types, And Functions
`DetermineSeed()` chooses a 31-bit cache hash seed from an explicit option, host name, or quasi-random process-unique generator. `ShardedCacheBase` implements `ComputePerShardCapacity()`, `GetPerShardCapacity()`, `NewId()`, `GetCapacity()`, default secondary-cache capacity/pinned usage accessors, `HasStrictCapacityLimit()`, `GetUsage(Handle*)`, and `GetPrintableOptions()`. `GetDefaultCacheShardBits()` chooses up to six shard bits based on capacity and a minimum shard size. `GetNumShardBits()` and `GetNumShards()` expose sharding geometry.

## Control Flow
Construction computes `shard_mask_` from `num_shard_bits`, chooses `hash_seed_`, stores strict capacity and total capacity, and initializes the ID counter. Capacity reads and strict-limit reads take `config_mutex_`; template-derived classes update those fields and then fan out per-shard changes. Printable options snapshot shared configuration under the same mutex and append subclass-specific options.

## State And Persistence Behavior
State is in-memory cache configuration: atomic `last_id_`, immutable shard mask and hash seed, and mutex-protected `strict_capacity_limit_` and `capacity_`. There is no persistence. `NewId()` provides monotonically increasing IDs for cache clients during the cache lifetime.

## Dependencies And Integration Points
The file depends on environment hostname lookup, unique ID generation, hash utilities, math helpers, and mutex utilities. It supports both `LRUCache` and HyperClock cache implementations through the template layer in `sharded_cache.h`.

## Risks And Edge Cases
Hash seed selection must remain bounded to 31 bits so users can reproduce diagnostics. Hostname lookup failure falls back to process-stable generated data. Per-shard capacity rounds up, so total shard capacity can exceed configured capacity by up to `num_shards - 1`. Default shard bits are capped at six to avoid over-sharding small or large caches.

## Test Signals
LRU and HyperClock tests indirectly validate shard capacity, strict-limit behavior, printable options, and table sizing. Tests using `NewCache()` with specific `num_shard_bits` validate that cache keys distribute correctly and async secondary-cache lookup works over multiple shards.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/sharded_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/sharded_cache.h -->
# sources/storage-engines/rocksdb/cache/sharded_cache.h

## Purpose
This header defines the generic sharded-cache framework used by RocksDB cache implementations. It separates non-template shared configuration from the template `ShardedCache<CacheShard>` adapter that maps public `Cache` operations to per-shard implementations.

## Important APIs, Types, And Functions
`CacheShardBase` documents the shard concept and provides defaults for metadata policy, hash type, hash computation, sharding hash extraction, and printable options. `ShardedCacheBase` declares shared public methods for IDs, capacity, strict limit, secondary-cache default accessors, printable options, hash seed, and shard geometry. `ShardedCache<CacheShard>` owns a cache-line-aligned shard array and implements `SetCapacity()`, `SetStrictCapacityLimit()`, `Insert()`, `CreateStandalone()`, `Lookup()`, `Erase()`, `Release()`, `Ref()`, usage/occupancy/table-address aggregation, `ApplyToAllEntries()`, `EraseUnRefEntries()`, `DisownData()`, and shard initialization/destruction helpers.

## Control Flow
Public operations compute a shard hash using `CacheShard::ComputeHash(key, hash_seed_)`, pick a shard with `HashPieceForSharding(hash) & shard_mask_`, and delegate to that shard. Capacity and strict-limit changes lock `config_mutex_`, update shared configuration, and apply per-shard updates. `ApplyToAllEntries()` rotates through shards with per-shard iteration states to limit lock hold time. The derived cache constructor must call `InitShards()` exactly once to placement-new each shard and enable destructor cleanup.

## State And Persistence Behavior
The template owns aligned shard memory and a boolean indicating whether shard destructors should run. Shared state in `ShardedCacheBase` is volatile cache configuration. `DisownData()` can intentionally leak shard data when heap allocations do not need freeing, avoiding shutdown-time destruction cost in supported builds.

## Dependencies And Integration Points
The header depends on `rocksdb/advanced_cache.h`, hash utilities, port alignment allocation, and mutex utilities. `LRUCache` derives from `ShardedCache<LRUCacheShard>`, and HyperClock cache types follow the same concept. Public cache factory options rely on this layer for sharding behavior.

## Risks And Edge Cases
The template assumes each shard implements the documented concept exactly; signature drift can produce difficult template errors. `ApplyToAllEntries()` currently clamps `average_entries_per_lock` with `std::min(aepl, 1)`, meaning it will use at most one average entry per lock regardless of a larger request, which is a behavior worth checking if iteration performance is changed. The aligned shard allocation must be paired with explicit shard destructor calls only after successful `InitShards()`.

## Test Signals
LRU tests validate shard operations through one-shard construction and public `NewCache()` wrappers. HyperClock tests stress sharded table sizing, capacity limits, and occupancy. Secondary-cache tests with `num_shard_bits=2` validate multi-shard async lookup and common cache-key prefix handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/sharded_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/tiered_secondary_cache.cc -->
# sources/storage-engines/rocksdb/cache/tiered_secondary_cache.cc

## Purpose
This file implements the lookup and promotion logic for `TieredSecondaryCache`, which stacks a compressed secondary cache in front of an NVM secondary cache. It lets lookups consult compressed memory first and then NVM, while optionally saving NVM-returned compressed data back into the compressed secondary tier.

## Important APIs, Types, And Functions
`TieredSecondaryCache::MaybeInsertAndCreate()` is the create callback used when an NVM lookup returns saved data; it may call `InsertSaved()` on the compressed secondary cache before delegating to the original helper's `create_cb`. `Lookup()` first queries the compressed secondary cache (`target()`), then wraps the original helper/context and queries `nvm_sec_cache_` using the tiered helper. `WaitAll()` waits outstanding NVM result handles and completes tiered result handles.

## Control Flow
Lookup starts in the compressed secondary tier. A compressed-tier hit returns immediately and marks `kept_in_sec_cache=true` so the primary adapter does not spill it back. On compressed miss, synchronous lookup uses a stack `CreateContext`; asynchronous lookup allocates a `ResultHandle` embedding that context, starts the NVM lookup, and returns the wrapper if the NVM lookup is pending or available. During create, `MaybeInsertAndCreate()` records either a compressed-secondary promotion or skip, then invokes the upper-layer helper to materialize the cache object.

## State And Persistence Behavior
The file manages no durable state directly. It passes through compressed data from NVM into the compressed secondary cache unless `advise_erase` is set or the data is uncompressed. It records stats ticks for promotions and skips. Async state is held in `ResultHandle` and its embedded `CreateContext` until `WaitAll()` completes it.

## Dependencies And Integration Points
The implementation depends on `cache/tiered_secondary_cache.h` and `monitoring/statistics_impl.h`. It is constructed by `NewTieredCache()` in `secondary_cache_adapter.cc` when an NVM secondary cache is configured with three-queue admission policy. It integrates the secondary-cache helper/create-callback contract with compressed-secondary `InsertSaved()`.

## Risks And Edge Cases
The implementation assumes NVM results represent `CacheTier::kVolatileTier` for now. Asynchronous lookup stores a pointer to the lookup key in the embedded context, so caller-managed key lifetime must remain valid for pending lookups. `kept_in_sec_cache` is forced true to avoid re-spill loops. `WaitAll()` must skip already-ready compressed-tier handles and only wait wrapped NVM handles.

## Test Signals
Compressed-secondary tiered tests exercise this through `NewTieredCache()` and admission policies. They validate promotion/skipping behavior indirectly via successful lookups, cache usage movement, and dynamic tiered-cache updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/tiered_secondary_cache.cc -->

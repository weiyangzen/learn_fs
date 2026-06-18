# subset-b-008713 Research

Grouped research report for RocksDB persistent cache, secondary index, simulator cache, and sorted run builder files. Each source section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier.cc -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier.cc

Purpose: implements `BlockCacheTier`, the persistent-cache tier that stores key/value cache records in rolling `.rc` files under `<path>/cache`, backed by in-memory metadata for key-to-LBA and cache-file lookup. It also exposes the `NewPersistentCache()` factory used by public persistent-cache setup.

Important APIs and control flow: `Open()` validates `PersistentCacheConfig`, creates/cleans the cache directory, creates the first `WriteableCacheFile`, and optionally starts `InsertMain()` for pipelined writes. `Insert()` either enqueues `InsertOp` into a bounded queue or calls `InsertImpl()` directly. `InsertImpl()` serializes under `lock_`, deduplicates by metadata lookup, appends to the current cache file, rolls to `NewCacheFile()` on EOF, inserts `BlockInfo`, and associates the block with the file for reverse eviction cleanup. `Lookup()` resolves key to `LBA`, resolves cache id to `BlockCacheFile`, reads and CRC-validates the record through the file layer, and updates hit/miss/error latency stats. `Reserve()` is called by writer threads before disk writes and evicts cold files until the requested write fits under a retained-size target.

State and persistence: persisted bytes live only in numbered `.rc` files, while all lookup metadata is process-local and rebuilt only by fresh inserts, not by scanning files. `Open()` removes existing cache files rather than recovering them. `Close()` stops the insert thread, stops writer threads, and clears metadata. `size_`, `writer_cache_id_`, `cache_file_`, and `metadata_` define the active cache state.

Dependencies and integration: depends on `BlockCacheTierMetadata`, `WriteableCacheFile`, `ThreadedWriter`, `BoundedQueue`, `StopWatchNano`, `Env`, logging, and sync points. It implements `PersistentCacheTier`, integrates with block-based table persistent cache through `NewPersistentCache()`, and uses `Reserve()` as the storage budget callback from `ThreadedWriter`.

Risks and test signals: metadata is volatile and cleanup-on-open means this is a persistent medium cache, not a durable reusable index. `Erase()` asserts that the key exists, so callers must not erase absent keys. `InsertMain()` drops inserts after retry exhaustion, and direct write failures can surface as `TryAgain`. Several stress and eviction tests in `persistent_cache_test.cc` are disabled; active coverage includes factory construction and DB integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier.h

Purpose: declares `BlockCacheTier`, the disk-backed `PersistentCacheTier` implementation, including its write pipeline queue, file writer, metadata manager, cache size accounting, and statistics.

Important APIs/types: public overrides include `Insert`, `Lookup`, `Open`, `Close`, `Erase`, `Reserve`, `IsCompressed`, `GetPrintableOptions`, `Stats`, and `TEST_Flush`. Private `InsertOp` carries queued key/value writes and a quit signal; `Statistics` stores histograms and atomic counters for pipelined bytes, written/read bytes, hit/miss/error counts, dropped inserts, and latencies.

Control flow and state: construction wires a bounded insert queue, a fixed write-buffer allocator sized from config, and a `ThreadedWriter`. `TEST_Flush()` waits for the insert queue to drain but does not explicitly wait for all file IO callbacks beyond the normal writer/file path. `lock_` protects metadata, active file replacement, and capacity reservation while file-level locks protect per-file buffers and readers.

Dependencies and integration: includes RocksDB cache/persistent-cache interfaces, histograms, mutex utilities, file and metadata headers, and `BoundedQueue`. It is the concrete tier used by `NewPersistentCache()` and by tiered RAM+block configurations.

Risks and test signals: raw pointer ownership is split between `cache_file_` and metadata, so close/evict paths must remain consistent. The class assumes config validation prevents buffer/file-size deadlocks. Pipelined queue overflow silently drops `InsertOp`s at `BoundedQueue` level, only later visible through miss behavior or dropped stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file.cc -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file.cc

Purpose: implements persistent-cache file primitives: cache record serialization, random-access reads, buffered append-only writes, file deletion, and the async writer pool used by `BlockCacheTier`.

Important APIs and control flow: `CacheRecord` encodes `{magic, crc, key_size, value_size, key, value}` and verifies CRC on read. `RandomAccessCacheFile::Open/Read/ParseRec` wrap `FSRandomAccessFile` in `RandomAccessFileReader` and deserialize records by `LBA`. `WriteableCacheFile::Create` opens a new writable file and establishes a file reference. `Append()` expands buffer slabs, records the LBA, serializes the record into buffers, advances `disk_woff_`, sets EOF when max size is reached, and dispatches full buffers. `DispatchBuffer()` pads partial EOF buffers for alignment and hands them to `ThreadedWriter`; `BufferWriteDone()` cascades dispatch and closes/reopens the file for reads after EOF.

State and persistence: in-flight files keep data in `CacheWriteBuffer` slabs and serve reads from memory until closed. Closed files are reopened through the random-access path. `BlockCacheFile::Delete()` asks `Env` for size then removes the `.rc` file. `ThreadedWriter` reserves cache capacity before appending buffer chunks to the writable file.

Dependencies and integration: uses `Env`, `FileSystem`, `WritableFile`, `FSRandomAccessFile`, `RandomAccessFileReader`, CRC32C, logging, direct IO options, `CacheWriteBufferAllocator`, and `PersistentCacheTier::Reserve`. `BlockCacheTier` owns file creation, cache-id assignment, metadata insertion, and eviction.

Risks and test signals: `NewWritableCacheFile()` ignores the `use_direct_writes` parameter in the current implementation, despite `Create()` accepting it. `DispatchIO()` appends `io_size_` slices without trimming the final slice, relying on buffer padding/alignment. CRC errors print diagnostic data to stderr and return read failure. Most persistent-cache file stress tests are disabled, so active coverage is mostly through the DB persistent-cache path.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file.h

Purpose: declares the logical block address, file abstraction hierarchy, and threaded writer interfaces for block-cache persistent files.

Important APIs/types: `LogicalBlockAddress` (`LBA`) identifies a record by cache id, file offset, and record size. `Writer` abstracts async buffer writes. `BlockCacheFile` owns common path/cache-id/block-info metadata and virtual `Append`/`Read`/`Delete`. `RandomAccessCacheFile` adds thread-safe disk reads and record parsing. `WriteableCacheFile` adds append buffering, in-memory reads while open, EOF transition, and close-to-read behavior. `ThreadedWriter` queues `IO` work items and dispatches them on worker threads.

Control flow and state: `WriteableCacheFile` tracks `buf_woff_` for the buffer being filled, `buf_doff_` for next dispatch, `pending_ios_`, `disk_woff_`, `eof_`, and `enable_direct_reads_`. Reads choose disk or buffer path based on whether EOF has occurred and buffers have been cleared. `ThreadedWriter::IO` includes a callback so the file can update pending state when a buffer write finishes.

Dependencies and integration: integrates with `CacheWriteBufferAllocator`, `LRUElement`, `PersistentCacheTier`, RocksDB file abstractions, and cache metadata via `BlockInfo`. `BlockCacheFile` inherits `LRUElement<BlockCacheFile>` so cache-file objects can be evicted by `EvictableHashTable`.

Risks and test signals: reference counts (`refs_`) are used both for lookup pinning and eviction safety; incorrect increments/decrements would block eviction or allow deletion while reading. The comment notes a write-pipeline architecture for high-throughput devices, but correctness depends on file-level serialization and buffer allocator sizing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file_buffer.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file_buffer.h

Purpose: provides fixed-size write buffers and a synchronized buffer pool for the persistent block-cache write path.

Important APIs/types: `CacheWriteBuffer` supports `Append`, `FillTrailingZeros`, `Reset`, `Free`, `Capacity`, `Used`, and `Data`. `CacheWriteBufferAllocator` preallocates a list of buffers, exposes nonblocking `Allocate`, `Deallocate`, `WaitUntilUsable`, and reports free/capacity based on buffers currently in the pool.

Control flow and state: `WriteableCacheFile::ExpandBuffer()` pulls buffers from the allocator, serializes records into them, and returns them through `ClearBuffers()` after file close. Pipelined insert retry waits on `WaitUntilUsable()` when allocation fails. The allocator uses a mutex and condition variable around the free-list.

Dependencies and integration: depends on RocksDB `port::Mutex`/`CondVar` via `util/mutexlock.h`. It is consumed by `WriteableCacheFile` and constructed by `BlockCacheTier` from `PersistentCacheConfig` sizing.

Risks and test signals: allocator `Capacity()` and `Free()` report only free-list bytes, not total originally allocated capacity, which is useful for pool availability but can surprise callers. `FillTrailingZeros()` writes ASCII `'0'` bytes, not zero bytes, which is acceptable for padding outside record ranges but is semantically unusual. Buffer-count validation in `PersistentCacheConfig` is the main deadlock guard.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_metadata.cc -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_metadata.cc

Purpose: implements the metadata manager joining block keys to logical addresses and cache-file ids to evictable file objects.

Important APIs and control flow: `Insert(BlockCacheFile*)` adds a file to the evictable file index. `Lookup(cache_id)` returns a file and relies on `EvictableHashTable::Find()` to increment `refs_`. `Insert(key,lba)` allocates `BlockInfo` and inserts it into the block index. `Lookup(key,lba)` obtains the striped read lock from `HashTable::Find()`, copies the LBA, and releases the lock. `Evict()` asks the file index for an LRU candidate and passes `RemoveAllKeys()` as a callback. `Clear()` deletes all file and block metadata.

State and persistence: all metadata is in memory. `RemoveAllKeys()` uses the file's reverse `block_infos()` list to erase every block index entry pointing at a file before the file is deleted. There is no on-disk metadata replay.

Dependencies and integration: wraps `HashTable<BlockInfo*>` and `EvictableHashTable<BlockCacheFile>`, using `BlockCacheFile`'s LRU/reference fields. `BlockCacheTier` calls it for insert, lookup, erase, eviction, and close.

Risks and test signals: `Remove()` asserts successful erase, so absent-key erases are not tolerated. `Lookup(cache_id)` leaves reference decrementing to callers after `Read()`. The active tests exercise hash table operations independently and persistent-cache lookup through DB tests; direct metadata eviction is covered mainly by disabled persistent-cache stress tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_metadata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_metadata.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_metadata.h

Purpose: declares `BlockInfo` and `BlockCacheTierMetadata`, the two-index metadata structure for disk-backed persistent cache.

Important APIs/types: `BlockInfo` stores a string key and `LBA`. `BlockCacheTierMetadata` exposes file insertion/lookup, block insertion/lookup/removal, LRU file eviction, and full clear. It defines hash/equality functors for cache ids and block keys.

Control flow and state: the cache-file index is an `EvictableHashTable` keyed by `BlockCacheFile::cacheid()`, giving lookup pinning and LRU eviction. The block index is a striped `HashTable` mapping `BlockInfo*` keys to the stored `BlockInfo*`. Reverse links from `BlockCacheFile::block_infos()` allow file eviction to remove all keys belonging to that file.

Dependencies and integration: includes `block_cache_tier_file.h`, `hash_table.h`, `hash_table_evictable.h`, and `lrulist.h`. It is private infrastructure for `BlockCacheTier`.

Risks and test signals: default capacities are fixed at 1M blocks and 10K files; workloads beyond that increase chain length because the hash table does not resize. Memory ownership is manual: inserts allocate `BlockInfo`, clear/evict/delete paths must free it exactly once.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table.h

Purpose: implements a fixed-size, striped-lock hash table optimized for concurrent persistent-cache metadata lookups.

Important APIs/types: template `HashTable<T, Hash, Equal>` provides `Insert`, `Find`, `Erase`, `GetMutex`, and `Clear`. `Find` has a special contract: it returns with the bucket read lock still held via `ret_lock`, so callers can safely inspect returned data until they unlock.

Control flow and state: construction computes bucket count from capacity/load factor, allocates bucket and lock arrays, and `mlock`s them on Linux. Operations hash the key to a bucket and then to one of `nlocks_` locks. Buckets use `std::list<T>` collision chains and no resizing. Destruction asserts all buckets have been cleared.

Dependencies and integration: used by `BlockCacheTierMetadata`, `EvictableHashTable`, volatile cache, tests, and the hash-table benchmark. It depends on RocksDB mutex wrappers and Linux `mlock` when available.

Risks and test signals: lack of resizing means bad capacity estimates degrade lookup/insert/erase latency. The lock handoff API is easy to misuse; failing to unlock after `Find` deadlocks a stripe. Unit tests cover million-key insert/lookup and erase behavior, but not concurrent correctness under thread sanitizer.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_bench.cc -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_bench.cc

Purpose: provides a gflags microbenchmark comparing a single-RWMutex `std::unordered_map` wrapper against the custom striped `HashTable`.

Important APIs/types: `HashTableImpl<Key,Value>` defines `Insert`, `Erase`, and `Lookup`. `HashTableBenchmark` prepopulates keys, spawns Env threads for writes/reads/erases, runs for `FLAGS_nsec`, and prints throughput. `SimpleImpl` wraps `unordered_map`; `GranularLockImpl` wraps `HashTable<Node, Hash, Equal>`.

Control flow and state: prepopulation inserts 1M stable read keys plus 10M additional keys, then writer threads append increasing keys, readers randomly verify prepopulated values, and erasers delete increasing keys. Atomic counters accumulate operation totals.

Dependencies and integration: built only outside Windows and requires gflags. Uses RocksDB Env threading, random utilities, port time helpers, and the persistent-cache hash table.

Risks and test signals: the benchmark asserts on failed inserts/reads, so it is a development tool rather than robust benchmark harness. The erase-failure percentage expression uses integer division before conversion. It does not write research-relevant artifacts and is not unit-test coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_evictable.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_evictable.h

Purpose: layers LRU eviction on top of the striped `HashTable` for pointer types, used by cache files and volatile cache entries.

Important APIs/types: `EvictableHashTable<T,Hash,Equal>` exposes `Insert`, `Find`, `Evict`, `Clear`, `GetMutex`, and debug LRU assertions. Each lock stripe has an `LRUList<T>`, and each object must inherit compatible `LRUElement` fields.

Control flow and state: insert adds to the hash bucket and pushes the object at the cold end of the stripe LRU. find increments `refs_` and touches the object to the hot end. eviction picks a random stripe start and scans stripes for an unreferenced LRU entry, erasing it from the bucket and optionally invoking a callback. clear unlinks every object from its stripe LRU and calls a deleter.

Dependencies and integration: depends on `HashTable`, `LRUList`, and `Random::GetTLSInstance()`. It is central to cache-file eviction in `BlockCacheTierMetadata` and RAM-key eviction in `VolatileCacheTier`.

Risks and test signals: callers must decrement `refs_` after using found objects; otherwise eviction can stall. Eviction is approximate across stripes, not global LRU. Tests validate bulk eviction returns valid values but do not assert exact ordering because stripe selection is randomized.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_evictable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_test.cc -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_test.cc

Purpose: unit tests for the custom `HashTable` and `EvictableHashTable` implementations used by persistent-cache metadata.

Important APIs/tests: `HashTableTest` defines value-type `Node` and tests inserting 1M key/value pairs plus lookup verification, then random erasure of 1024 keys and full verification. `EvictableHashTableTest` defines pointer-type `Node` inheriting `LRUElement` and checks that 1M inserted nodes can all be evicted with intact values.

Control flow and state: tests explicitly clear maps in fixture destructors, satisfying the hash table destructor's empty-bucket assertions. Lookup tests use the returned read lock and unlock it after checking the copied node.

Dependencies and integration: uses RocksDB test harness, DB test utilities, random utilities, and the persistent-cache hash/LRU templates.

Risks and test signals: coverage is single-threaded despite the implementation targeting multi-core contention. Eviction ordering is intentionally not checked. The tests are expensive enough to allocate many large strings, so they are functional correctness signals rather than lightweight regression tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/lrulist.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/lrulist.h

Purpose: implements an intrusive LRU list with reference-aware eviction for persistent-cache data structures.

Important APIs/types: `LRUElement<T>` provides `next_`, `prev_`, and atomic `refs_`. `LRUList<T>` exposes `Push`, `Unlink`, `Pop`, `Touch`, and `IsEmpty`. The list treats `head_` as cold and `tail_` as hot.

Control flow and state: `Push()` inserts at the cold head. `Touch()` unlinks an element and appends it at the hot tail. `Pop()` scans from `head_` until it finds an element with `refs_ == 0`, unlinks it, and returns it; referenced entries are skipped. All list mutations take a `port::Mutex`.

Dependencies and integration: used by `EvictableHashTable`, with element storage embedded in `BlockCacheFile` and `VolatileCacheTier::CacheData`.

Risks and test signals: intrusive pointers require each object to be present in at most one list and correctly unlinked before destruction. The list lock nests inside hash-table stripe locks in evictable table operations, so lock ordering must remain stable. Tests indirectly cover push/touch/evict through `hash_table_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/lrulist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_bench.cc -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_bench.cc

Purpose: gflags benchmark driver for persistent-cache tiers: disk block cache, volatile RAM cache, and tiered volatile+block cache.

Important APIs/types: factory helpers build `VolatileCacheTier`, `BlockCacheTier`, or `PersistentTieredCache` from flags. `CacheTierBenchmark` optionally prepopulates one million keys, starts write/read threads, runs for `FLAGS_nsec`, prints local latency/byte histograms and cache stats, flushes, and closes the cache.

Control flow and state: keys are fixed 24-byte binary slices from three `uint64_t`s, values are deterministic byte patterns of `FLAGS_iosize`. Writers insert monotonically increasing keys; readers pick random keys below `read_key_limit_`. `Prepop()` also warms reads before timed stats.

Dependencies and integration: requires gflags, uses RocksDB histograms, system clock, Env logging, block builder include, and persistent-cache tier implementations. It is operational tooling for tuning `writer_iosize`, queue depth, pipelining, cache size, and tier mix.

Risks and test signals: with `GFLAGS` absent the file builds a stub main. It asserts on lookup status unless benchmark mode only relaxes content verification. `NewVolatileCache()` passes `FLAGS_cache_size` to the first constructor argument of `VolatileCacheTier`, which is `is_compressed`, not `max_size`, so this helper appears suspect in this snapshot. Bench results are not correctness tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_test.cc -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_test.cc

Purpose: implements persistent-cache unit and DB integration tests, plus helper factories for volatile, block, and tiered cache configurations.

Important APIs/tests: helpers `NewTieredCache`, `NewBlockCache`, `MakeVolatileCache`, `MakeBlockCache`, and `MakeTieredCache` create concrete tiers. `FactoryTest` actively validates `NewPersistentCache()` for NVM and non-NVM options and checks stats availability. `PersistentCacheDBTest.BasicTest` actively runs a DB/table integration using block persistent cache. Many direct tier stress tests for insertion, eviction, tiering, and file-create error are disabled due to cost/environment constraints.

Control flow and state: Linux sync points disable `O_DIRECT` and mock unique-id behavior for test environments. DB tests create a column family with block-based table persistent cache, write compressible data, flush to SST, read twice, and assert persistent-cache hit/miss tickers were exercised.

Dependencies and integration: uses `DBTestBase`, block-based table options, transaction-free DB reads/writes, `SyncPoint`, file utilities, and `BlockCacheTier`.

Risks and test signals: active tests validate integration more than exhaustive eviction/file-IO behavior. Disabled tests are still valuable as design intent for stress, direct writes, volatile eviction, block eviction, and tiered cache behavior. Sync-point callbacks are platform-sensitive and Linux-specific.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_test.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_test.h

Purpose: declares test fixtures and reusable workloads for persistent-cache tier and DB tests.

Important APIs/types: `PersistentCacheTierTest` provides `Flush`, thread spawn/join helpers, threaded `Insert` and `Verify`, padded key generation, and test templates for normal, negative, and eviction-enabled insert runs. `PersistentCacheDBTest` extends `DBTestBase` and provides ticker access, `Insert`, `Verify`, and `RunTest`.

Control flow and state: tier tests generate `key_prefix_` keys and 4KB deterministic values, retry `TryAgain` inserts, flush queued writes, then verify hits/misses across threads. DB tests write into a secondary column family named `pikachu`, disable block cache for default CF, flush to SST, and read values twice to exercise cache behavior.

Dependencies and integration: includes RocksDB DB test utilities, block builder/table options, test harness, random, and volatile cache. It is included by `persistent_cache_test.cc`.

Risks and test signals: workload helpers assume absent lookup during eviction means acceptable eviction, while non-eviction paths require every key to be present. The destructor closes any remaining cache, so tests that already close reset `cache_` to avoid double use. Most direct tier tests using this fixture are disabled in the implementation file.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_tier.cc -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_tier.cc

Purpose: implements shared persistent-cache configuration printing, base tier pass-through behavior, tiered-cache forwarding, and cache id generation.

Important APIs and control flow: `PersistentCacheConfig::ToString()` emits all tunables. `PersistentCacheTier::Open/Close/Stats/TEST_Flush` delegate to `next_tier_` by default; `Reserve` and `Erase` default to success. `PrintStats()` formats each tier's stats map. `NewId()` returns a relaxed atomic increment. `PersistentTieredCache` forwards `Open`, `Close`, `Erase`, `Stats`, `PrintStats`, `Insert`, `Lookup`, and `IsCompressed` to the front tier; `AddTier()` chains the prior tail to the new tier.

State and persistence: `PersistentTieredCache::Close()` clears `tiers_` only after the front close succeeds. Base tiers hold only `next_tier_` and `last_id_`; persistence is implemented by concrete tiers.

Dependencies and integration: sits under `BlockCacheTier` and `VolatileCacheTier`, and implements the common `PersistentCache` API defined in RocksDB headers.

Risks and test signals: `PersistentTieredCache::next_tier()` and `set_next_tier()` use `auto it = tiers_.end(); return (*it)...`, which dereferences end and appears erroneous if called. Normal forwarding uses `tiers_.front()` and `AddTier()` uses `tiers_.back()`, so the risky functions may be rarely exercised. Factory and DB tests validate common open/close/stats paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_tier.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_tier.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_tier.h

Purpose: defines persistent-cache configuration and the abstract tiering model for volatile and persistent storage tiers.

Important APIs/types: `PersistentCacheConfig` carries `Env`, clock, path, logger, direct IO flags, cache/file/write-buffer sizes, writer queue depth, pipelining controls, dispatch size, and compression mode. `ValidateSettings()` enforces non-null path/env, cache/file/buffer sizing, queue depth, and dispatch alignment. `PersistentCacheTier` extends `PersistentCache` with lifecycle, reserve/erase, recursive stats, next-tier chaining, and `TEST_Flush`. `PersistentTieredCache` presents a chain of tiers as one cache.

Control flow and state: concrete tiers implement `Insert`, `Lookup`, `IsCompressed`, and options printing. Tier chains pass misses/evictions downward depending on concrete behavior. `write_buffer_count()` computes enough slabs based on writer depth and cache file size to avoid pipeline deadlock.

Dependencies and integration: included by all persistent-cache tier implementations and exposed through RocksDB table options via `PersistentCache`.

Risks and test signals: validation catches several deadlock-prone configurations, but the unused `MakePersistentCacheConfig` declaration has no implementation in this file set. The tiered cache API expects at least one tier and asserts otherwise. Header comments contain typos but document intended RAM/NVM/SSD tiering.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_tier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_util.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_util.h

Purpose: provides `BoundedQueue<T>`, a simple synchronized queue used by persistent-cache insert and writer pipelines.

Important APIs/types: `Push(T&&)` appends unless the configured byte-size bound would be exceeded, `Pop()` waits until an item exists and returns it by move, and `Size()` returns tracked queued bytes. The item type must provide `Size()`.

Control flow and state: queue size is updated by item size on push/pop, with a mutex and condition variable around the list. Overflow silently drops the pushed item rather than returning status.

Dependencies and integration: used for `BlockCacheTier::InsertOp` and `ThreadedWriter::IO`. Depends on RocksDB mutex and condition variable wrappers.

Risks and test signals: silent overflow is intentional for cache best-effort semantics but means callers cannot directly count drops at enqueue time. `SignalAll()` is used on each push, which is simple but can wake more waiters than needed. Coverage is indirect through persistent-cache tests and benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/volatile_tier_impl.cc -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/volatile_tier_impl.cc

Purpose: implements `VolatileCacheTier`, an in-memory LRU persistent-cache tier that can spill evicted entries to the next tier.

Important APIs and control flow: `Insert()` pre-adds value size to `size_`, evicts until within `max_size_`, inserts a `CacheData` into the evictable hash index, and rolls size back on duplicate/eviction failure. `Lookup()` finds the key, copies the value to caller-owned memory, decrements the reference count, and returns hit; on miss it delegates to `next_tier()` if present. `Evict()` removes an LRU entry, optionally inserts it into the next tier, decrements `size_`, and deletes it. `Stats()` returns hit/miss/insert/evict counters and percentages.

State and persistence: state is entirely memory resident: `index_`, `size_`, `max_size_`, and stats. Persistence only occurs if a lower tier accepts evicted data. Destruction clears the index and deletes all `CacheData`.

Dependencies and integration: uses `EvictableHashTable`, `LRUElement`, and `PersistentCacheTier` next-tier chaining. It is used in tiered RAM+block cache tests and benchmark setup.

Risks and test signals: `Erase()` is unsupported and asserts. Duplicate inserts return `TryAgain` rather than success. `Evict()` ignores next-tier insert errors, which is acceptable for a cache but can lose data from upper-tier perspective. Most volatile/tiered stress tests are disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/volatile_tier_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/volatile_tier_impl.h -->
# sources/storage-engines/rocksdb/utilities/persistent_cache/volatile_tier_impl.h

Purpose: declares the RAM-backed `VolatileCacheTier` implementation of `PersistentCacheTier`.

Important APIs/types: public methods include `Insert`, `Lookup`, `IsCompressed`, `Erase`, `GetPrintableOptions`, and `Stats`. Private `CacheData` stores immutable key and value strings and inherits `LRUElement`. Hash/equality functors drive an `EvictableHashTable<CacheData>`.

Control flow and state: `max_size_` and `size_` are atomics used for coarse capacity accounting. `Statistics` stores atomic hit/miss/insert/evict counters and computes hit/miss percentages. Eviction is LRU through the index/list combination.

Dependencies and integration: depends on persistent-cache tier abstractions and the persistent-cache hash/LRU templates. It can be used standalone or as the front tier in `PersistentTieredCache`.

Risks and test signals: comments say the evictable hash table is not concurrent at this point, while the tier uses atomics for counters/size; concurrent behavior depends on the underlying striped locks and correct ref handling. The constructor defaults to unlimited capacity, making eviction optional unless configured.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/persistent_cache/volatile_tier_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/faiss_ivf_index.cc -->
# sources/storage-engines/rocksdb/utilities/secondary_index/faiss_ivf_index.cc

Purpose: implements `FaissIVFIndex`, a RocksDB secondary index that stores FAISS IVF inverted-list entries in a RocksDB secondary column family and queries them through a `SecondaryIndexIterator`.

Important APIs/types: helper functions serialize FAISS list labels as varint signed integers. `FaissIVFIndex::Adapter` implements `faiss::InvertedLists` with iterator-based reads and `add_entry` writes into a string context. `IteratorAdapter` seeks a secondary iterator to one list label, validates values as FAISS codes, maps transient FAISS ids to primary keys, and feeds code pointers to FAISS search. Public methods set/get primary and secondary column families, transform primary column values into list labels, build secondary key prefixes, encode secondary values, and perform KNN search.

Control flow and state: construction replaces the FAISS index's inverted lists with the RocksDB adapter and forces `parallel_mode = 0`. On writes, `UpdatePrimaryColumnValue()` assigns the input vector to a coarse list and stores the label as the primary column's indexed value; `GetSecondaryValue()` calls `index_->add_core()` to generate the code stored under `label + primary_key`. On search, FAISS probes lists using `SearchParametersIVF::inverted_list_context`, which lets the adapter enumerate RocksDB entries on demand.

Dependencies and integration: depends on FAISS `IndexIVF`, `InvertedLists`, RocksDB `SecondaryIndex`, `SecondaryIndexIterator`, `ConvertSliceToFloats`, `autovector`, and varint coding. Integrated through `SecondaryIndexMixin`/TransactionDB secondary-index hooks.

Risks and test signals: code assumes vector slices are exactly `index_->d` floats and secondary values are exactly `code_size`. Iterator value pointers point into RocksDB iterator-owned storage and must remain valid until FAISS consumes them. Exceptions from FAISS/iterator code are converted to RocksDB status. Tests compare against a native FAISS baseline and cover invalid KNN arguments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/faiss_ivf_index.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/faiss_ivf_index_test.cc -->
# sources/storage-engines/rocksdb/utilities/secondary_index/faiss_ivf_index_test.cc

Purpose: integration tests for `FaissIVFIndex` using TransactionDB secondary indices and FAISS IVF Flat indexes.

Important tests: `Basic` trains an IVF index, writes 1024 embeddings as wide-column entities, verifies secondary column-family keys decode into valid list labels and primary ids, verifies values equal original embeddings for `IndexIVFFlat`, runs KNN searches for original vectors, and checks invalid search arguments. `Compare` trains a RocksDB-backed and native FAISS index on the same data, inserts 4096 vectors, and compares result ids/distances over multiple neighbors/probe counts and query vectors.

Control flow and state: tests create primary/secondary column families manually, set them on the index, and wrap a raw RocksDB iterator in `SecondaryIndexIterator` for KNN. Primary keys are decimal ids, which simplifies parsing returned secondary suffixes.

Dependencies and integration: uses FAISS random/vector/index classes, TransactionDB, secondary-index public headers, RocksDB test harness, and coding utilities.

Risks and test signals: coverage is strong for IVF Flat search equivalence and argument validation, but it does not cover deletes/updates of FAISS-indexed rows or non-flat/code-compressed IVF variants. It assumes bytewise ordering compatible with `SecondaryIndexIterator` prefix seeking.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/faiss_ivf_index_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_helper.h -->
# sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_helper.h

Purpose: provides conversion helpers for secondary-index APIs that accept either borrowed `Slice` or owned `std::string` in `std::variant`.

Important APIs/types: `SecondaryIndexHelper::AsSlice()` visits the variant and returns a `Slice` view. `AsString()` returns an owned `std::string`, copying a `Slice` or returning the existing string.

Control flow and state: no persistent state; functions are pure variant visitors. `AsSlice()` relies on the caller preserving variant lifetime when the active alternative is `std::string`.

Dependencies and integration: uses RocksDB `Slice`, namespace headers, and `util/overload.h`. It is used by `SecondaryIndexMixin`, `SecondaryIndexIterator`, and `SimpleSecondaryIndex`.

Risks and test signals: misuse of a returned `Slice` after the variant/string dies would dangle. The helper centralizes conversions, reducing repeated visitor code across secondary-index components.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_iterator.cc -->
# sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_iterator.cc

Purpose: implements `SecondaryIndexIterator`, a prefix-scoped wrapper over a normal RocksDB iterator for scanning one secondary-index key prefix.

Important APIs and control flow: construction stores a `SecondaryIndex` and underlying iterator. `Seek(target)` asks the index to finalize the target prefix, stores it as an owned string, and seeks the underlying iterator to that prefix. `Valid()` requires OK wrapper status, underlying validity, and key prefix match. `key()` strips the prefix from the underlying key, while `value`, `columns`, `timestamp`, `PrepareValue`, `Next`, `Prev`, `status`, and `GetProperty` delegate to the underlying iterator.

State and persistence: iterator state is transient: `prefix_`, `status_`, index pointer, and underlying iterator. It does not write data.

Dependencies and integration: used by FAISS KNN search to enumerate one or more inverted lists and by consumers of public secondary-index APIs. It depends on `SecondaryIndexHelper` for variant conversion.

Risks and test signals: the code has a FIXME that prefix seeking works for `BytewiseComparator` but not arbitrary comparators. `Prev()` can step outside the prefix and then `Valid()` becomes false. Tests exercise forward scans indirectly through FAISS.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_mixin.h -->
# sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_mixin.h

Purpose: template mixin that adds secondary-index maintenance to transaction-like write APIs by intercepting puts, entity puts, deletes, and single deletes.

Important APIs/types: overrides tracked/untracked `Put`, `PutEntity`, `Delete`, `SingleDelete`, and SliceParts variants. `Merge` and `MergeUntracked` return not supported. `IndexData` records an applicable `SecondaryIndex`, the previous primary column value, and an optional updated primary column value produced by the index. `PerformWithSavePoint()` wraps mutations so failures roll back to a transaction save point.

Control flow and state: put paths lock/read existing primary entity with `GetEntityForUpdate`, remove old secondary entries, let applicable indices update primary column values, write the primary entry with `assume_tracked`, then add secondary entries. Delete paths read existing columns, remove secondary entries, then perform primary delete/single-delete. Secondary keys are finalized prefix plus primary key; secondary values are optional and default to empty.

Dependencies and integration: depends on RocksDB transaction methods supplied by `Txn`, wide-column helpers, `SecondaryIndex` public interface, and `SecondaryIndexHelper`. It is the core write-side bridge used by TransactionDB options carrying secondary indices.

Risks and test signals: secondary-entry remove uses `SingleDelete`, so correctness depends on one existing version per secondary key under transaction semantics. All existing secondary entries for a row are removed/recreated even if unchanged. Merge is not supported. Tests for FAISS cover put/entity insertion, but update/delete behavior needs separate coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/secondary_index_mixin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/simple_secondary_index.cc -->
# sources/storage-engines/rocksdb/utilities/secondary_index/simple_secondary_index.cc

Purpose: implements a simple secondary index whose secondary key prefix is the indexed primary column value encoded as a length-prefixed slice.

Important APIs and control flow: constructor stores the primary column name. Setters/getters bind primary and secondary column families. `UpdatePrimaryColumnValue()` leaves the primary value unchanged. `GetSecondaryKeyPrefix()` returns the primary column value, `FinalizeSecondaryKeyPrefix()` encodes it with `PutLengthPrefixedSlice`, and `GetSecondaryValue()` leaves the secondary value empty.

State and persistence: state is only the configured column handles and column name; persisted secondary data is maintained by `SecondaryIndexMixin` in the secondary column family as finalized prefix plus primary key.

Dependencies and integration: uses public `secondary_index_simple.h`, varint/length-prefixed coding, and `SecondaryIndexHelper`.

Risks and test signals: the implementation assumes secondary key ordering over length-prefixed values is acceptable for equality/prefix scans, not arbitrary value-range ordering. Empty secondary values mean all payload must come from primary lookup or key suffix. Coverage is likely through broader secondary-index tests outside this file set.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/secondary_index/simple_secondary_index.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator.cc -->
# sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator.cc

Purpose: implements trace-driven block-cache simulators that replay `BlockCacheTraceRecord` events against simulated LRU caches and report miss-ratio statistics for different policies.

Important APIs and control flow: `GhostCache::Admit()` implements second-hit admission. `CacheSimulator::Access()` performs ordinary block lookup/insert and updates metrics. `MissRatioStats::UpdateMetrics()` aggregates total/user accesses, misses, and per-second timelines. `PrioritizedCacheSimulator` assigns high priority to filter/index/uncompression-dictionary blocks and centralizes `AccessKVPair()`. `HybridRowBlockCacheSimulator` models row-key-value caching for Get requests, using `get_id` state to skip later block accesses after a row hit. `BlockCacheTraceSimulator::InitializeCaches()` builds configured simulator instances, including ghost variants, and `Access()` handles warmup reset and fanout.

State and persistence: simulation state lives in RocksDB `Cache` instances, optional ghost caches, miss-ratio counters, per-Get row status maps, and simulator configuration maps. No persistent output is written here; consumers read stats from objects.

Dependencies and integration: uses LRU cache factory, block cache tracer records/helpers, trace enums, RocksDB cache priority, and `ExtractUserKey` through trace helpers. It supports policies named `lru`, `lru_priority`, `lru_hybrid`, and `lru_hybrid_no_insert_on_row_miss`, optionally prefixed with `ghost_`.

Risks and test signals: timestamp variable names mix milliseconds/microseconds, but code divides microsecond trace timestamps by `kMicrosInSecond`. `downsample_ratio_` is used as a divisor without explicit zero validation. Hybrid state can grow by `get_id` count. Tests cover ghost admission, basic/prioritized/hybrid policies, no-insert behavior, row-key insertion, and ghost-hybrid behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator.h -->
# sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator.h

Purpose: declares cache simulator configurations, miss-ratio statistics, admission policy helpers, and simulator classes for block-cache trace replay.

Important APIs/types: `CacheConfiguration` identifies cache name, shard bits, ghost capacity, and capacity sweep values, with comparison operators for map keys. `MissRatioStats` exposes reset, total/user miss ratios, counters, timelines, and `UpdateMetrics`. `GhostCache` controls second-access admission. `CacheSimulator`, `PrioritizedCacheSimulator`, `HybridRowBlockCacheSimulator`, and `BlockCacheTraceSimulator` form the simulator hierarchy.

Control flow and state: base simulator tracks one simulated cache plus optional ghost cache. Prioritized simulator adds priority classification and shared lookup/insert helper. Hybrid simulator tracks per-Get completion and row-key insertion state. Trace simulator owns a map from configuration to capacity-specific simulator objects and manages warmup.

Dependencies and integration: includes LRU cache and block-cache tracer headers. It is used by simulator tests and by tooling that consumes RocksDB block-cache traces.

Risks and test signals: `CacheConfiguration::operator==` ignores `cache_capacities`, while `operator<` also ignores it; this groups all capacities under one configuration key by design because values live in the mapped vector. Callers must avoid zero downsample ratios. Unit tests exercise most declared simulator classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator_test.cc -->
# sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator_test.cc

Purpose: unit tests for trace-driven cache simulators and hybrid row/block cache behavior.

Important tests: helper methods generate user Get and compaction trace records and assert simulated cache contents. Tests cover `GhostCache` second-hit admission, base `CacheSimulator` user/non-user stats and no-insert compaction behavior, ghost simulator miss behavior, prioritized simulator insertion, hybrid row/block behavior across repeated Gets and different referenced keys, small-cache eviction behavior, no-insert-on-row-miss mode, and ghost-hybrid admission.

Control flow and state: tests use deterministic block keys, referenced row keys, get ids, and small or large LRU capacities. They inspect both simulator counters and underlying simulated cache entries to verify row and block insertions.

Dependencies and integration: uses RocksDB test harness, Env timestamps, trace records, `ExtractUserKey`, and LRU cache options.

Risks and test signals: tests strongly cover simulator policy semantics but do not test `BlockCacheTraceSimulator::InitializeCaches()` invalid-name or warmup reset paths directly. Some miss ratios are compared after integer casts because ratios are floating point percentages.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/cache_simulator_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/sim_cache.cc -->
# sources/storage-engines/rocksdb/utilities/simulator_cache/sim_cache.cc

Purpose: implements `SimCache`, a wrapper cache that forwards real cache operations to a target cache while maintaining a separate key-only simulated cache and optional activity log.

Important APIs and control flow: internal `CacheActivityLogger` starts/stops bounded logging, writes `LOOKUP` and `ADD` lines, tracks background status, and auto-stops on max size or error. `SimCacheImpl::Insert()` inserts key-only metadata into the simulated cache if absent, logs the add, then forwards the real insert to `target_` if present. `Lookup()` and `StartAsyncLookup()` call `HandleLookup()` to update simulated hit/miss counters/tickers and log lookups before forwarding. Capacity, strict limit, usage, pinned usage, erase, value, id, helper, and iteration APIs delegate to the target cache while sim-capacity/usage APIs address the key-only cache.

State and persistence: state includes `key_only_cache_`, atomic hit/miss counters, optional target stats pointer use, and activity log file writer. The activity log is persistent on disk until caller removes it; cache contents are normal cache memory state.

Dependencies and integration: uses RocksDB cache API, LRU cache factory, statistics tickers, writable file writer, Env/FileSystem, mutexes, and public `rocksdb/utilities/sim_cache.h`. `NewSimCache()` builds the key-only LRU cache with metadata charge disabled.

Risks and test signals: `stats_` member is initialized null and reset_counter sets ticker counts through it; per-lookup stats are recorded from the lookup call instead. Several methods assume `target_` is non-null, while `Insert/Lookup` tolerate null; construction from public factory normally supplies target. `num_shard_bits >= 20` returns null. Tests validate counters, strict capacity interaction, simulated usage, and activity logging size bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/sim_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/sim_cache_test.cc -->
# sources/storage-engines/rocksdb/utilities/simulator_cache/sim_cache_test.cc

Purpose: DB integration tests for the `SimCache` wrapper and its activity logging.

Important tests: `SimCache` configures tiny block sizes, wraps a real LRU in `NewSimCache`, loads blocks through iterators, checks real block-cache tickers and simulated hit/miss counters, validates simulated usage equals real usage while pinned, exercises strict capacity failure, releases iterators, and verifies later accesses become sim hits. `SimCacheLogging` starts activity logging, reads flushed blocks twice, counts `LOOKUP` and `ADD` log lines, then verifies auto-stop near a max log size.

Control flow and state: tests use `DBTestBase`, build block-based table options with `block_cache = simCache`, write enough small values to create block entries, and inspect both cache counters and filesystem log contents.

Dependencies and integration: uses public sim-cache header, block-based table factory, DB test utilities, stack trace handler, LRU cache options, and RocksDB statistics.

Risks and test signals: strong integration coverage for cache wrapper behavior in real DB reads, including strict capacity and logging. Tests rely on predictable block creation with `block_size = 1`, which can be sensitive to table-format behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/simulator_cache/sim_cache_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/sorted_run_builder/sorted_run_builder.cc -->
# sources/storage-engines/rocksdb/utilities/sorted_run_builder/sorted_run_builder.cc

Purpose: implements `SortedRunBuilder`, a utility that ingests unsorted key/value data into a temporary RocksDB instance and emits a compacted sorted run as SST files.

Important APIs and control flow: `SortedRunBuilderImpl::Open()` configures a temporary DB with `VectorRepFactory`, universal compaction, disabled auto-compactions, caller-specified memory/file-size/compression/table/comparator options, WAL disabled for writes, and bulk-load-friendly settings. `Add()` and `AddBatch()` write without WAL and update relaxed entry/data counters. `Finish()` flushes all memtables, forces optimized compaction, collects output file paths and post-compaction metadata stats, and marks the builder finished. `NewIterator()` is allowed only after finish. `Cleanup()`/destructor destroy the temp DB unless `keep_temp_db` is set.

State and persistence: persisted intermediate/output state is the temporary DB directory. Output SST paths are returned after compaction. `finished_`, `cleaned_up_`, relaxed counters, `db_`, and `output_files_` define lifecycle state. WAL is disabled, so resumability is based on flushed SSTs rather than log replay.

Dependencies and integration: uses RocksDB DB, memtable rep, table factory, write batch, filename separator, comparator, and atomic utilities. Public construction is through `SortedRunBuilder::Create()`, which validates options before opening the temp DB.

Risks and test signals: temp directory must not preexist because `error_if_exists = true`. Concurrent `Add()` calls are not explicitly synchronized beyond DB internals; `allow_concurrent_memtable_write` is false. Cleanup uses comparator in `DestroyDB` but not all original options. Finish cannot be called twice, and adding after finish is invalid. A separate `sorted_run_builder_test.cc` exists outside this work item and likely carries functional coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/sorted_run_builder/sorted_run_builder.cc -->

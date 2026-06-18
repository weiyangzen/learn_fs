# Research Group subset-b-008584

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_block_cache_test.cc -->
# sources/storage-engines/rocksdb/db/db_block_cache_test.cc

## Purpose

`db_block_cache_test.cc` is a RocksDB gtest suite for the block-based table block cache contract. It exercises cache insertion, lookup, eviction, strict capacity behavior, pinning, entry-role statistics, cache warming during flush and compaction, compression dictionary blocks, secondary cache type coverage, cache key stability, and cache-key encoding. The file is not production code; it is an integration-heavy regression suite that drives `DBTestBase` through real DB opens, flushes, compactions, external file ingestion, checkpoints, and iterator reads while observing `Statistics`, cache occupancy, and block cache internals.

The tests intentionally cover several block roles: data blocks, index blocks, filter blocks, filter/index metadata partitions, compression dictionary blocks, write-buffer dummy entries charged through cache, and cache-entry stats collector entries. They also verify behavior across LRU and HyperClock cache implementations, partitioned and unpartitioned metadata, runtime options, and cache keys based on SST unique IDs.

## Important APIs, Types, and Helpers

The main fixture is `DBBlockCacheTest : DBTestBase`. It provides `GetTableOptions()` with a tiny `block_size` so each key-value pair tends to occupy its own data block, `GetOptions()` wiring statistics and a block-based table factory, `InitTable()` for a fixed ten-key data set, and counter helpers around `BLOCK_CACHE_*` and `BLOCK_CACHE_COMPRESSION_DICT_*` tickers. `GetCacheEntryRoleCountsBg()` reads `DB::Properties::kFastBlockCacheEntryStats` and parses role counts through `BlockCacheEntryStatsMapKeys`.

Custom cache/test adapters are central to the suite:

- `PersistentCacheFromCache` implements `PersistentCache` backed by a regular typed cache for compressed persistent-cache coverage when Snappy is enabled.
- `ReadOnlyCacheWrapper` rejects block cache inserts.
- `PriorityTrackingCache` records `Cache::Priority` for cache warming inserts.
- `MockCache` subclasses `LRUCache` and counts high/low priority inserts.
- `LookupLiarCache` wraps a cache and can force a particular lookup to return not found, simulating a race where an insert becomes redundant.
- `StableCacheKeyTestFS` disables file unique IDs and hard links so cache key stability can be tested through copied/checkpointed DBs using table properties.
- `CacheKeyTest` constructs synthetic `TableProperties`, calls `BlockBasedTable::SetupBaseCacheKey()` / `BlockBasedTable::GetCacheKey()`, and uses local decoding helpers to validate the 128-bit cache-key encoding.
- `DBBlockCachePinningTest` parameterizes partitioned metadata and three `PinningTier` knobs: top-level index, partition blocks, and unpartitioned metadata.

The suite depends on RocksDB internals from `cache/*`, `table/block_based/*`, `db/db_impl/*`, `table/unique_id_impl.h`, `env/unique_id_gen.h`, fault injection FS wrappers, and sync points. It also uses `Checkpoint`, `SstFileWriter`, `ExportImportFilesMetaData`, `WriteBufferManager`, `DB::GetMapProperty`, and direct cache APIs such as `Insert`, `Lookup`, `EraseUnRefEntries`, `ApplyToAllEntries`, `SetCapacity`, `SetStrictCapacityLimit`, `GetUsage`, `GetPinnedUsage`, and `GetOccupancyCount`.

## Control Flow and Test Coverage

The early tests validate basic data-block cache lifecycle. `IteratorBlockCacheUsage` opens an iterator with `fill_cache=false`, seeks into a table, observes nonzero usage while the iterator pins a block, then verifies usage returns to zero after delete. `TestWithoutCompressedBlockCache` fills an empty-capacity LRU cache with pinned iterator blocks, shrinks capacity to current usage, enables strict capacity, and verifies the next seek fails with `MemoryLimit` and increments add-failure stats. After releasing pinned iterators, subsequent reads hit the cache without inserts.

`IndexAndFilterBlocksOfNewTableAddedToCache` and `IndexAndFilterBlocksStats` validate eager caching of index/filter blocks after table creation when `cache_index_and_filter_blocks` and Bloom filters are enabled. They assert index/filter miss and add counters after flush, then prove later `KeyMayExist` and `Get` calls hit cached metadata. The stats variant checks byte insertion counters and cache usage for metadata blocks.

The cache warming tests cover `BlockBasedTableOptions::prepopulate_block_cache`. `WarmCacheWithDataBlocksDuringFlush` verifies flush-only warming adds data blocks and avoids read misses, while compaction does not add more under flush-only settings. `WarmCacheWithDataBlocksDuringCompaction` uses `PriorityTrackingCache` and `kFlushAndCompaction`: flush inserts are low priority, compaction output data blocks are inserted at bottom priority, and reads after compaction miss no data blocks. `DBBlockCacheTest1.WarmCacheWithBlocksDuringFlush` parameterizes full filters versus partitioned filters and verifies data, index, filter, and compression dictionary related cache stats during flush warming, including the doubled metadata counts for partitioned filter/index layouts.

`DynamicOptions` changes the block-based table factory string at runtime to switch `prepopulate_block_cache` among `kFlushOnly`, `kDisable`, and `kFlushAndCompaction`. It demonstrates that new flushes observe the updated option while existing data remains readable; the test documents unsupported dynamic cache replacement cases as commented-out expected failures.

Priority and paranoia coverage follows. `IndexAndFilterBlocksCachePriority` checks `cache_index_and_filter_blocks_with_high_priority`; index/filter blocks respect the configured priority while data blocks remain low priority. `ParanoidFileChecks` verifies that with `paranoid_file_checks=true`, table creation/compaction reads data blocks and populates cache, and that disabling the option dynamically stops those additional cache inserts.

`CacheCompressionDict` iterates block-based format versions 6 and 7 and every supported compression. For compression algorithms that support dictionaries, bottommost compaction creates dictionary blocks, preloads them, and later reads hit the cached dictionary plus index while only the data block is missed/inserted. Unsupported dictionary compressions must still avoid crashes/corruption.

`CacheEntryRoleStats` is a large role-accounting integration test over partitioned/unpartitioned metadata and LRU/HyperClock caches. It clears cache entries except the stats collector, performs misses and hits that load filters, index blocks, data blocks, and write buffer reservations, then validates `kFastBlockCacheEntryStats` and `kBlockCacheEntryStats`. It uses mock time to check background versus foreground refresh intervals, simulates a long scan to stretch refresh timing, confirms a pinned stats collector survives a full cache, and injects DB mutex lock/unlock during cache scans to check the scan path is not holding the DB mutex.

`HyperClockCacheReportProblems` fills a HyperClock cache with fake entries at expected, smaller, and larger than estimated sizes. It captures info-log messages via `CountingLogger` to verify periodic stats report no warnings in normal range, warnings/errors when the configured estimated value size is too small, and info/warning when it is too high.

`DBBlockCacheTypeTest` runs against all testing cache types from `secondary_cache_test_util`. `AddRedundantStats` uses `LookupLiarCache` to create redundant index, filter, and data block insert attempts and validates per-role redundant add counters plus aggregate `BLOCK_CACHE_ADD_REDUNDANT`. `Uncache` parameterizes partitioned metadata and `options.uncache_aggressiveness`. It proves obsolete blocks are removed after non-trivial compaction when aggressiveness is nonzero, preserved when disabled, preserved across reopen without cache churn, and not incorrectly uncached on trivial move compactions.

The cache key tests validate persistence and encoding invariants. `StableCacheKeys` runs with and without original file numbers in table properties. It creates ordinary SSTs, external ingested SSTs, exports a column family, reopens, copies via checkpoint, imports into a different DB, and re-ingests external files. When original file numbers are present, cache stats show stable key reuse across these operations; when missing, stats intentionally grow because cache key reuse is unsafe. `DBImplSessionIdStructure` checks generated session IDs share high bits in a process and differ in low counter bits. `CacheKeyTest.Encodings` constructs a base key and brute-forces many combinations of session counter bits, file number bits, and offset bits whose total fits in 128 bits. The local decoder reconstructs all original fields, validating the uniqueness claim in `cache_key.cc`.

`DBBlockCachePinningTest.TwoLevelDB`, compiled with LZ4, builds an L0 and L1 file with enough metadata to partition index/filter blocks and with an L1 compression dictionary. It erases unpinned blocks and then reads from L0 and L1, computing expected metadata/dictionary misses from the selected `PinningTier` settings. The test distinguishes `kNone`, `kFlushedAndSimilar`, and `kAll`, and treats compaction-created L1 metadata differently from flush-created L0 metadata.

## State and Persistence Behavior

The suite repeatedly persists state to SST files through `Flush()`, moves files through `CompactRange()`, imports/exports files, and reopens DBs with different options. The important persistent state under test is not user values but table metadata: filter/index blocks, compression dictionary blocks, table properties such as `orig_file_number`, DB/session IDs, external SST unique IDs, and block-based table format versions. Cache contents are process-local and intentionally survive `Reopen(options)` when the same cache object is reused; several tests assert this persistence of in-memory cache state across DB close/open, while also verifying obsolete-file cache entries are dropped after compaction when configured.

The cache-key path is especially persistence-sensitive. Stable cache keys are derived from table properties and internalized SST unique IDs so identical SST files in checkpoints, exports, imports, and external ingestion can reuse cache entries. The control case with missing file numbers proves the implementation degrades safely by avoiding reuse rather than risking collision.

## Dependencies and Integration Points

These tests integrate with block-based table readers/builders, Bloom filter metadata, compression dictionary training, compaction, flush, table cache, secondary cache type factories, checkpoint/export/import flows, external SST ingestion, cache-entry statistics collectors, `Statistics` tickers, `PerfContext` indirectly through reads, `SyncPoint` injection, and the mocked environment clock. They also rely on compile-time feature gates: Snappy for persistent compressed-cache helper coverage, Linux/Windows for warming tests under one block, and LZ4 for dictionary/pinning tests.

## Risks and Edge Cases

The file protects against regressions in cache accounting, redundant insertion races, strict-capacity failure handling, iterator pin lifetime, stale cache stats, DB mutex deadlocks during cache scans, incorrect cache priority, accidental compaction cache warming, incorrect trivial-move uncaching, compression dictionary cache misses/corruption, and cache key collisions across DB copies/imports. A notable risk in this suite is tight coupling to exact ticker increments and cache occupancy. Changes in table metadata layout, filter partitioning, cache metadata charging, or compaction file layout can require careful test updates even when user-visible behavior is still correct.

## Test Signals

The strongest signals are exact `Statistics` ticker assertions for `BLOCK_CACHE_*`, `BLOCK_CACHE_INDEX_*`, `BLOCK_CACHE_FILTER_*`, `BLOCK_CACHE_DATA_*`, compression dictionary counters, redundant add counters, cache entry role counts, and byte insertion counters. Cache object signals include `GetUsage`, `GetPinnedUsage`, `GetOccupancyCount`, `EraseUnRefEntries`, `ApplyToAllEntries`, and insert priority observations. Behavioral signals include `Get`, `KeyMayExist`, iterator validity/status, compaction level counts, no cache churn after reopen, log severity counts for HyperClock cache warnings, and stable cache stats across checkpoint/export/import workflows.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_block_cache_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_bloom_filter_test.cc -->
# sources/storage-engines/rocksdb/db/db_bloom_filter_test.cc

## Purpose

`db_bloom_filter_test.cc` is the main RocksDB DB-level test suite for Bloom-like table filters, prefix filters, memtable Bloom filters, Ribbon filters, filter construction memory charging, filter construction corruption detection, dynamic filter/prefix options, and experimental SST query filters. It drives real DB operations and validates both correctness and performance-oriented signals such as random read counts, Bloom useful counters, block cache filter accesses, and per-level perf context counters.

The file covers unpartitioned filters, coupled partitioned filters, decoupled partitioned filters, legacy Bloom, fast local Bloom, standard Ribbon, auto Bloom/Ribbon policies, plain table prefix Bloom stats, and block-based format versions from legacy values through the latest format. It also tests unusual comparator/prefix-extractor combinations to ensure newer prefix-filtering logic no longer depends on old, overly strict prefix axioms.

## Important APIs, Types, and Helpers

The base fixture is `DBBloomFilterTest : DBTestBase`. It stores a `FilterPartitioning` enum and provides `PartitionFilters()` plus `SetInTableOptions()` to configure partitioned filters and two-level indexes. Parameterized fixtures add format/filter settings: `DBBloomFilterTestWithPartitioningParam`, `DBBloomFilterTestWithFormatParams`, `DBBloomFilterTestDefFormatVersion`, `DBBloomFilterTestVaryPrefixAndFormatVer`, `BloomStatsTestWithParam`, `ChargeFilterConstructionTestWithParam`, and `DBFilterConstructionCorruptionTestWithParam`.

Important helper types include:

- `Create(bits_per_key, name)`, which delegates to `BloomLikeFilterPolicy::Create()` for named Bloom/Ribbon implementations.
- `SliceTransformLimitedDomainGeneric` and `SliceTransformLimitedDomain`, which test prefix extractors with restricted domains.
- `AlwaysTrueBitsBuilder` / `AlwaysTrueFilterPolicy`, which produce a constructed filter with 100 percent false-positive behavior or skip filter construction by returning `nullptr`.
- `CompatibilityConfig`, which writes files using different built-in filter policies and format versions, then reads them through every compatible reader policy.
- `LevelAndStyleCustomFilterPolicy` and `TestingContextCustomFilterPolicy`, which choose filter builders based on `FilterBuildingContext` and log context fields.
- `BackwardBytewiseComparator`, `FixedSuffix4Transform`, `WeirdComparator`, and `NonIdempotentFixed4Transform`, which intentionally violate obsolete prefix-extractor assumptions.
- Experimental `KeySegmentsExtractor`, `SstQueryFilterConfigs`, `SstQueryFilterConfigsManager`, and segment query filter factories used by the SST query filter tests.

The suite observes tickers including `BLOOM_FILTER_USEFUL`, `BLOOM_FILTER_PREFIX_USEFUL`, `BLOOM_FILTER_PREFIX_CHECKED`, `BLOOM_FILTER_FULL_POSITIVE`, `BLOOM_FILTER_FULL_TRUE_POSITIVE`, `BLOOM_FILTER_PREFIX_TRUE_POSITIVE`, `BLOCK_CACHE_FILTER_HIT/MISS`, `BLOCK_CACHE_FILTER_BYTES_INSERT`, `NON_LAST_LEVEL_SEEK_FILTER_MATCH`, `NON_LAST_LEVEL_SEEK_FILTERED`, `NON_LAST_LEVEL_SEEK_DATA`, and `NON_LAST_LEVEL_SEEK_DATA_USEFUL_FILTER_MATCH`. It also reads `get_perf_context()` fields such as memtable/SST Bloom hits/misses and per-level `bloom_filter_useful`.

## Control Flow and Test Coverage

`KeyMayExist` verifies the point-read existence API with high bits-per-key filters, partitioned and unpartitioned variants, and full block cache. It covers absent keys, memtable hits with value found, flushed table lookups that avoid file opens and block cache additions, deleted keys, compaction, and delete tombstones.

`GetFilterByPrefixBloomCustomPrefixExtractor` and `GetFilterByPrefixBloom` build prefix-only SST filters. They check that present keys and same-prefix absent keys do not increment useful counters, while absent keys with prefixes missing from the filter increment `BLOOM_FILTER_PREFIX_USEFUL` and per-level perf counters. They also demonstrate that `total_order_seek` no longer affects `Get()`, and that changing the prefix extractor disables use of older incompatible prefix filters both dynamically and after reopen.

`FilterNumEntriesCoalesce` writes repeated versions under snapshots, with whole-key and prefix filtering toggled. It validates table property `num_filter_entries` counts unique whole keys and unique prefixes rather than every internal entry. `WholeKeyFilterProp` is an extensive mixed-file test that toggles whole-key and prefix filtering across reopen and compaction. It proves files are only queried through filters they actually contain, mixed prefix/whole-key files are handled correctly, and useful counters reflect which file/filter combination pruned a lookup.

`BloomFilter` is a large randomized access/performance test over format/filter parameters. It writes 10,000 keys, compacts to multiple layers, adds a small L0 update file, disables compactions triggered by seeks, and counts random reads for present and absent lookups. The expected bounds differ for partitioned filters because partition filters and partition indexes add reads when no block cache is used. The test also validates aggregated table properties such as `filter_size` and `num_filter_entries`, with different size expectations for Bloom versus auto Ribbon.

`SkipFilterOnEssentiallyZeroBpk` covers filter omission. Bits-per-key below 0.5 and a custom policy returning no builder must produce zero filter size and no full-filter counters. The control policy constructs an always-true filter so reads check it and increment positive/true-positive counters. It also verifies old generated options strings such as `rocksdb.BuiltinBloomFilter`: existing filters can be read, but new filters are not generated when configuration details are unknown. `FilterBitsBuilderDedup` directly tests builder de-duplication of whole keys and alternate keys/prefixes through `EstimateEntriesAdded()`.

`BloomFilterRate` uses `ChangeFilterOptions()` to verify high useful rates for missing keys in a wide SST key range, including per-level perf context. `BloomFilterCompatibility` writes one SST for each built-in filter/format combination, then reopens with each reader configuration and asserts all built-in readers can read all built-in filter encodings, producing positives for existing keys and useful negatives for absent keys.

`ChargeFilterConstructionTestWithParam.Basic` verifies filter construction memory charging through cache reservations for disabled/enabled decisions, Bloom versus Ribbon, full versus partitioned filters, legacy Bloom exclusion, and corruption-detection mode. It sizes key counts around `CacheReservationManagerImpl<CacheEntryRole::kFilterConstruction>::GetDummyEntrySize()` so dummy cache-reservation entries are observable. The assertions validate peak count and approximate reservation size for hash entries, final filters, and Ribbon banding. This test is explicitly expensive and documents its disk/time cost.

`DBFilterConstructionCorruptionTestWithParam.DetectCorruption` uses sync points to tamper with hash entries and finished filter bytes during filter construction. With `detect_filter_construct_corruption` enabled, flush returns `Status::Corruption()` with specific diagnostics; disabled cases succeed. `DynamicallyTurnOnAndOffDetectConstructCorruption` then changes the block-based table factory option at runtime, proving the detection flag can be enabled and disabled dynamically.

`ContextCustomFilterPolicy` validates `FilterBuildingContext`. The custom policy changes bits per key based on compaction style and creation level and records column family name, compaction style, level count, creation level, bottommost flag, and table-file creation reason. The test covers FIFO and level compaction, flush-created files, compacted bottommost files, and external SST file creation through `SstFileWriter`, then checks false-positive-rate-derived useful counters match the selected bits-per-key policy.

`MutatingRibbonFilterPolicy` verifies `RibbonFilterPolicy` has mutable `bloom_before_level` and that `SetOptions` mutates the existing filter policy object rather than replacing it. `MutableFilterPolicy` verifies `BlockBasedTableOptions::filter_policy` can be replaced dynamically with Ribbon, Bloom, null, and serialized Ribbon option strings; subsequent flushed files show expected filter bytes per key.

The memtable tests cover both correctness and memory accounting. `PrefixExtractorWithFilter1/2` cover limited-domain prefix extractors for point reads and iterators. `MemtableWholeKeyBloomFilter` checks prefix-only versus whole-key memtable Bloom behavior and proves whole-key filtering can operate without a prefix extractor. `MemtableWholeKeyBloomFilterMultiGet` combines memtable Bloom, `MultiGet`, snapshots, flushed data, and range deletes. `TestMemtableBloomAndWBM` verifies write-buffer-manager-backed cache accounting for memtable Bloom memory and that pinned old memtables keep their Bloom allocations after flush. `MemtablePrefixBloom` exercises Get, Seek, SeekForPrev, dynamic prefix extractor changes, existing versus new memtables, and in-domain/out-of-domain behavior.

`PartitionedMultiGet` tests partitioned filters for `MultiGet` across full-key and prefix modes and format versions 2-5. It verifies correct statuses, true-positive/useful counters, and that a clump of keys loads a single filter partition while spread-out keys load many partitions without duplicate partition loads. It also seeks clumps spanning two partitions.

`BloomStatsTest` and `BloomStatsTestWithIter` check perf-context Bloom hit/miss counters for memtable and SST filters using both `Get()` and iterators. They run over legacy Bloom, fast local Bloom, partitioning variants, and plain table.

`PrefixScan` builds an LSM shape with 11 SST files whose ranges overlap a target prefix. With prefix Bloom and `prefix_same_as_start` when required, scanning a prefix reads only the two relevant files, validating the intended random-I/O reduction.

`OptimizeFiltersForHits` exercises `options.optimize_filters_for_hits`. It first creates a level-compaction shape with last-level files lacking filters and verifies useful filter counts for misses across upper levels. It then rewrites the last level with filters and shows that when the optimization is disabled, bottom-level filter blocks are cached and hit on repeated reads; when enabled, bottom-level filter blocks are ignored for point reads, open-time preloading, trivial moves to bottom level, and iterators.

The dynamic prefix-filter tests are `DynamicBloomFilterUpperBound`, `DynamicBloomFilterMultipleSST`, `DynamicBloomFilterNewColumnFamily`, and `DynamicBloomFilterOptions`. They create SST files with different prefix extractor configurations, change prefix extractors with `SetOptions`, use `iterate_upper_bound` and `prefix_same_as_start` to determine whether old filters are compatible, and verify old iterators retain their original prefix semantics. The tests count `NON_LAST_LEVEL_SEEK_FILTER_MATCH` and `NON_LAST_LEVEL_SEEK_FILTERED` to prove filters are checked, skipped, or used to prune at the right times.

`SeekForPrevWithPartitionedFilters` guards reverse iteration over partitioned filters by seeking before every key boundary with both whole-key filtering on and off. The weird prefix extractor tests validate that prefix filtering works with suffix extraction, reverse comparators, non-idempotent transforms, and comparators whose ordering of prefixes differs from full keys. These cases cover both memtable and flushed SST Bloom paths and use bounds/auto-prefix mode where appropriate.

Finally, `SstQueryFilter` and `FixedWidthSegments` cover experimental SST query filters. `SstQueryFilter` defines a delimiter-based segment extractor, min/max segment filters scoped by key categories, a versioned configs manager, and range-query table filters. It verifies config version behavior, per-file filter writing, runtime version changes, pruning of lower/higher level files by segment ranges, portability across alternate config names/extractors, and non-last-level seek data counters. `FixedWidthSegments` unit-tests capped fixed-width segment extraction IDs and segment sizes, then uses reverse-bytewise min/max segment filters with reverse comparator range queries to verify filtering for short keys, empty segments, and selected segment ranges.

## State and Persistence Behavior

The suite persists Bloom-like filters into SST table properties and metadata blocks during flush, compaction, and external SST creation. It repeatedly reopens DBs under different table factories and prefix extractors to verify old filter metadata remains readable only when compatible. Dynamic options apply only to newly created tables or newly created iterators where appropriate; existing iterators keep their old prefix/filter semantics, and existing memtable Bloom filters can be bypassed after prefix extractor changes until a fresh memtable is created.

Several tests depend on mixed persisted state: some SSTs contain prefix filters, some whole-key filters, some partitioned filters, some Ribbon filters, some no filters, and some experimental SST query filter properties. The expected behavior is conservative: use persisted filters when the current policy can read them and their prefix/query configuration is compatible; otherwise skip them without false negatives.

## Dependencies and Integration Points

This file integrates with block-based and plain table factories, Bloom/Ribbon filter policies, `FilterBitsBuilder`, `FilterBuildingContext`, table properties, table property collectors, cache reservation managers, cache entry roles, DB dynamic options, `PerfContext`, per-level perf context, `Statistics`, `SyncPoint`, `SstFileWriter`, compaction, snapshots, range deletes, `MultiGet`, iterators, prefix extractors, custom comparators, write buffer manager cache charging, and experimental range-query filtering APIs.

## Risks and Edge Cases

The tests protect against false negatives, incompatible prefix-filter reuse, wrong useful/positive counters, excessive random reads, incorrect filter-size accounting, double-counted filter entries, broken built-in filter compatibility, construction memory under-accounting, missed corruption detection, dynamic option mutation bugs, stale iterator semantics, invalid use of old prefix axioms, partitioned-filter duplicate loading, bottom-level filter caching when optimized for hits, and experimental query-filter version/config portability errors.

The suite is sensitive to implementation details such as filter partition sizes, cache-line rounding, dummy cache-reservation entry sizes, compaction output levels, and false-positive-rate bands. Changes to filter encoding, partition sizing, table property names, or compaction heuristics can require updating numerical thresholds while preserving the core no-false-negative and compatibility guarantees.

## Test Signals

Primary correctness signals are exact `Get`, `KeyMayExist`, `MultiGet`, iterator, snapshot, range-delete, and range-query results. Performance and integration signals include random read counter bounds, Bloom useful/checked/positive/true-positive tickers, block cache filter hit/miss/add-byte counters, non-last-level seek filter/data counters, memtable and SST perf-context Bloom hit/miss counters, aggregated table properties, cache reservation peak/increment sequences, `Status::Corruption()` text from construction tampering, and `FilterBuildingContext` trace strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_bloom_filter_test.cc -->

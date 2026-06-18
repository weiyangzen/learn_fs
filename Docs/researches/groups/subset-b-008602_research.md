# subset-b-008602 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_properties_test.cc -->
# sources/storage-engines/rocksdb/db/db_properties_test.cc

## Purpose
`db_properties_test.cc` is a RocksDB DB-layer regression suite for property reporting. It verifies the public `DB::GetProperty`, `DB::GetIntProperty`, `DB::GetAggregatedIntProperty`, `DB::GetMapProperty`, `DB::GetPropertiesOfAllTables`, and table-properties collector contracts across memtables, SST files, caches, compression sampling, FIFO oldest-key time, write stalls, and table metaindex layout.

The file is test code, but it acts as a behavioral specification for how in-memory state, persisted table metadata, cache accounting, and internal statistics are surfaced through string, integer, aggregate, map, and table-property APIs.

## Important APIs, Types, And Functions
The main fixture is `DBPropertiesTest : public DBTestBase`, constructed with database name `db_properties_test` and `env_do_fsync=false`. Its helper `AssertDbStats()` validates map entries returned by `DB::Properties::kDBStats`, including uptime, WAL bytes, user bytes, self/other write counts, WAL-enabled write counts, and write-stall micros.

Important helper functions include `VerifySimilar()`, `VerifyTableProperties()`, and `GetExpectedTableProperties()`. These compare parsed `TableProperties` output with estimated expected sizes and exact raw-key/raw-value/entry/delete/range-delete/merge counters. `PopMetaIndexKey()` consumes metaindex iterator keys and turns iterator status into stable assertion output.

Local table-property collectors are central test scaffolding. `CountingUserTblPropCollector` writes encoded user properties `CountingUserTblPropCollector` and `Count`. `CountingUserTblPropCollectorFactory` checks the `TablePropertiesCollectorFactory::Context::column_family_id` and tracks collector creation. `CountingDeleteTabPropCollector` counts point deletes, exposes `NeedCompact()` after more than ten deletes, and persists a readable `num_delete` property. `BlockCountingTablePropertiesCollector` increments `NumSampledBlocks` when compression-sampling callbacks report compressed block-size estimates.

The tests cover many public property constants: memtable counts and sizes, `kCurrentSuperVersionNumber`, `kSizeAllMemTables`, `kEstimateTableReadersMem`, block/blob cache capacity/usage/pinned usage, `kAggregatedTableProperties`, `kAggregatedTablePropertiesAtLevel`, `kNumImmutableMemTableFlushed`, `kEstimatePendingCompactionBytes`, compression ratio by level, `kEstimateOldestKeyTime`, total/live/obsolete SST sizes, `kMinObsoleteSstNumberToKeep`, `kBlockCacheEntryStats`, `kDBWriteStallStats`, and `kCFWriteStallStats`.

## Control Flow
The early tests validate simple property semantics. `Empty` creates an extra column family, checks active memtable entry counts before and after puts, blocks SST sync to observe memtable rollover, and validates nested `DisableFileDeletions()`/`EnableFileDeletions()` reference counting through `rocksdb.is-file-deletions-enabled`. `CurrentVersionNumber` proves the super-version number does not change on a write-only memtable update but increases after flush. `GetAggregatedIntPropertyTest` manually sums per-CF memtable sizes, compares the aggregate API, rejects non-integer aggregate properties, and verifies table-reader memory rises after flushes.

Table-property tests generate deterministic flushed files. `AggregatedTableProperties` writes puts, merges, and range deletes with Bloom filters and disabled auto-compaction, parses the aggregate table-property string, and compares exact logical counters plus approximate data/index/filter/block sizes. `AggregatedTablePropertiesAtLevel` compacts after each table, sums every per-level property string, and compares the sum to the global aggregate property.

Memtable tests drive state transitions. `NumImmutableMemTable` fills oversized write buffers with WAL disabled, checks active and immutable memtable entry/delete counters, uses perf-context memtable lookup counts to prove reads walk the expected number of memtables, flushes and verifies flushed immutable count, then exercises estimate-num-keys after updates and deletes. `ConcurrentWriteMemTableProperties` writes puts, deletes, and single deletes from four threads through the concurrent memtable path and relies on `flush_verify_memtable_count` to catch counter corruption during flush.

The disabled `DISABLED_GetProperty` test is a broad blocked-background-thread scenario. It pauses high/low priority background work, creates immutable memtables and pending flush/compaction states, checks the string and integer forms of pending/estimate properties, observes table-reader memory before and after reopening with limited `max_open_files`, and verifies `rocksdb.num-live-versions` changes while iterators pin old versions.

Later tests focus on persistence-derived properties. `ApproximateMemoryUsage` distinguishes current active/unflushed memtable bytes from retained memtables pinned by iterators and verifies the retained value shrinks as iterators are deleted and resets on reopen. `EstimatePendingCompBytes` blocks compaction, creates L0 pressure, checks pending compaction bytes rise, then resumes and checks the value returns to zero. `EstimateCompressionRatio` uses no-compression L0 and Snappy-compressed L1 data to assert level compression-ratio reporting.

Collector tests validate integration with table creation. `GetUserDefinedTableProperties` writes four SSTs and sums collector counts from `GetPropertiesOfAllTables()`, then compacts and checks collectors are created for compaction output. `UserDefinedTablePropertiesContext` repeats flush, automatic compaction, and manual compaction for a non-default CF and the default CF, proving the collector factory sees the correct column-family ID. `TablePropertiesNeedCompactTest` and `NeedCompactHintPersistentTest` verify `NeedCompact()` hints trigger compaction and survive DB reopen.

Compression-sampling tests use `BlockAddForCompressionSampling` and parameterized `EstimateDataSizeWithCompressionSampling` to assert `BlockAdd()` is called only when `sample_for_compression` is enabled and that fast/slow compression estimated data sizes are populated according to available libraries and chosen compression type. `EstimateNumKeysUnderflow` guards against negative estimates after repeated deletes.

FIFO and SST-size tests drive time and file lifecycle. `EstimateOldestKeyTime` uses a mock clock and FIFO compaction TTL to check oldest-key-time only exists for FIFO, advances as old files expire, and disappears when no FIFO files remain. `SstFilesSize` reads total/live/obsolete SST size properties before, during, and after file-deletion disablement around compaction, including a listener callback during compaction completion. `MinObsoleteSstNumberToKeep` checks that compaction output table numbers are reflected by the minimum obsolete SST number property while output files are being created.

Cache and map-property tests cover non-table state. `BlobCacheProperties` and `BlockCacheProperties` insert unpinned and pinned cache entries into configured LRU caches and verify capacity, usage, eviction, and pinned usage. `BlockCacheProperties` also asserts cache properties are unavailable for plain/cuckoo tables and block-based tables with `no_block_cache=true`. `GetMapPropertyDbStats` uses `MockSystemClock` and WAL-enabled/disabled writes to validate map-valued DB stats. `GetMapPropertyBlockCacheEntryStats` checks the exact role-key surface for block-cache entry stats. `WriteStallStatsSanityCheck` validates enum/string/stat mapping coverage, and `GetMapPropertyWriteStallStats` coerces DB-scope and CF-scope write stalls through write-buffer-manager and memtable-limit conditions.

The final `TableMetaIndexKeys` test opens the generated SST directly through the filesystem, reads the metaindex block with `ReadMetaIndexBlockInFile()`, and hard-codes expected metaindex keys for Bloom filters, partitioned filters, hash index metadata/prefixes, format-version-6 index block, and `rocksdb.properties`.

## State And Persistence Behavior
The suite observes transient in-memory state, persisted table metadata, manifest-visible file state, and cache-global state. Memtable properties depend on active/immutable transitions, retained memtables pinned by iterators, flushed immutable counters, delete counters, and concurrent write post-processing. SST properties depend on table-property blocks persisted at flush/compaction time, file level placement, table-reader cache load state, FIFO creation timestamps, obsolete-file deletion gating, and compaction output file numbers.

Several tests explicitly cross reopen boundaries. `ValidateSampleNumber` compares sampled estimate-num-keys with ground truth after reopening with `max_open_files=-1`. `NeedCompactHintPersistentTest` relies on a table-property `NeedCompact()` hint surviving restart so auto-compaction runs even below the L0 file-count trigger. `EstimateOldestKeyTime` uses mock elapsed time over flush and compaction cycles. `ApproximateMemoryUsage` and the disabled property test check table-reader and memtable retained-state reset or lazy-load behavior after reopen.

Cache properties are not per-CF persisted state. Block-cache aggregation sees a shared block cache across column families, while blob-cache and block-cache tests insert synthetic cache handles directly and assert DB property readers report the cache object's live capacity/usage/pinned counters. Pinned handles may temporarily allow usage to exceed capacity until released.

Write-stall map properties depend on internal DB/CF counters, not on table files. The tests distinguish DB-scope write-buffer-manager stalls from CF-scope memtable-limit stalls and require the map keys to expose the cause/condition matrix consistently.

## Dependencies And Integration Points
This file depends on `db/db_test_util.h`, `db/write_stall_stats.h`, `options/cf_options.h`, public RocksDB options/table/listener/perf APIs, block/table internals (`table/block_based/block.h`, `table/format.h`, `table/meta_blocks.h`, `table/table_builder.h`), `test_util/mock_time_env.h`, random utilities, string parsing helpers, and GoogleTest.

Integration points include `InternalStats::ppt_name_to_info`, property dispatchers for string/int/map properties, `DBImpl` aggregate property routing across column families, `ColumnFamilyData` and super-version changes, memtable implementations including concurrent skiplist writes, block-based table factory options, table property collection during flush and compaction, compression libraries, FIFO compaction, event listeners, LRU cache accounting, write-buffer-manager stalls, write-stall enum/stat mappings, the table cache/table-reader memory estimator, and direct filesystem/table metaindex parsing.

## Risks
Property tests are sensitive to internal accounting and option defaults. Counter changes in memtables, retained memtable sizing, table-reader memory estimates, cache metadata charging, compression-estimate fields, or write-stall enum ordering can break these tests even when high-level DB behavior remains correct. The file mitigates some estimator variability with bias-based comparison but still expects exact logical counters.

The custom collector tests guard important extension points. A regression in `TablePropertiesCollectorFactory::Context`, collector creation during compaction, `NeedCompact()` persistence, or `BlockAdd()` compression-sampling calls can silently break user-defined table metadata unless these tests fail.

Stateful tests can be timing-sensitive. Background-thread blocking, pending compaction bytes, flush-pending flags, and read-latency histograms depend on compaction scheduling, table-reader preloading, and `max_open_files` behavior. Sync-point and sleeping-task usage reduces but does not eliminate sensitivity.

Hard-coded compatibility assertions are deliberate risks. `TableMetaIndexKeys` protects metaindex key naming compatibility and will fail on legitimate format-key churn until the compatibility decision is updated. `WriteStallStatsSanityCheck` similarly forces enum, string, and internal-stat mappings to stay synchronized.

## Test Signals
Strong success signals include exact string/int property values for memtable entries/deletes, aggregate memtable sums matching manual per-CF sums, aggregate table-property logical counters matching generated data, per-level table properties summing to global properties, pending compaction bytes rising and returning to zero, FIFO oldest-key time advancing with file expiry, and cache capacity/usage/pinned properties matching direct LRU cache operations.

Other high-value signals are successful extraction of user-collected table properties, collector creation on flush and compaction with correct CF IDs, persisted need-compaction hints causing compaction after reopen, compression-sampling fields matching sampled blocks and selected compression library, obsolete SST size appearing only while file deletions are disabled, write-stall maps distinguishing DB-scope from CF-scope stalls, and stable metaindex key ordering for generated SSTs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_properties_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_range_del_test.cc -->
# sources/storage-engines/rocksdb/db/db_range_del_test.cc

## Purpose
`db_range_del_test.cc` is RocksDB's extensive regression suite for range deletion tombstones. It specifies `DB::DeleteRange()` semantics, unsupported configurations, flush and compaction behavior, snapshot visibility, merge-operand interactions, iterator reseek and sentinel-key behavior, file-boundary handling, compensated range-deletion size accounting, and error propagation.

The file is especially important because range tombstones are represented across multiple layers: memtables, immutable memtables, SST range-deletion blocks, `RangeDelAggregator`, `MergingIterator`, level iterators, compaction outputs, file metadata, table properties, and read options such as snapshots, upper bounds, and `ignore_range_deletions`.

## Important APIs, Types, And Functions
The primary fixture is `DBRangeDelTest : public DBTestBase`, using database name `db_range_del_test` and `env_do_fsync=false`. It adds `GetNumericStr(int)`, which encodes integers as eight-byte `uint64_t` keys for tests using `test::Uint64Comparator()`.

The main public API under test is `db_->DeleteRange(WriteOptions(), ColumnFamilyHandle*, begin, end)`, plus `WriteBatch::DeleteRange()` and unsupported `WriteBatchWithIndex::DeleteRange()`. The tests heavily use `Put`, `Merge`, `Delete`, `Flush`, `CompactRange`, `CompactFiles`, `MoveFilesToLevel`, `NumTableFilesAtLevel`, `FilesPerLevel`, `Get`, `NewIterator`, `GetSnapshot`/`ReleaseSnapshot`, `SetOptions`, and `GetPropertiesOfAllTables()`.

Internal/test integration APIs include `dbfull()->TEST_CompactRange()`, `RunManualCompaction()`, `TEST_GetFilesMetaData()`, `TEST_GetLevelIterator()`, `TEST_WaitForFlushMemTable()`, `TEST_WaitForCompact()`, `TablesRangeTombstoneSummary()`, `TableCache::Evict()`, `ColumnFamilyHandleImpl::cfd()`, `SuperVersion`, `MergeIteratorBuilder`, `InternalIterator`, `InternalKey`, `IterKey`, `RangeDelAggregator` behavior observed through iterator results, and perf-context counter `internal_range_del_reseek_count`.

Local helper and mock types cover specific risks. `MockMergeOperator` is intentionally non-associative. `SingleKeySstPartitioner` and `SingleKeySstPartitionerFactory` force partitions after every key. `TombstoneTestSstPartitioner` and its factory force a partition around `Key(5)`. `VerifyIteratorReachesEnd()` and `VerifyIteratorKey()` compactly assert iterator state and key sequences.

## Control Flow
The first tests establish API boundaries. Non-block-based table configurations and row cache reject range deletion, and `WriteBatchWithIndex` returns not-supported. Empty `[start, start)` ranges cover nothing, while `end < start` returns invalid argument and leaves data intact. Flush and compaction can emit files containing only range tombstones, including dictionary-compressed output, as long as snapshots protect tombstones from becoming obsolete.

Flush and compaction removal tests create puts around a tombstone and verify covered keys disappear while keys outside the half-open range, newer keys, and snapshot-visible keys remain. `FlushRangeDelsSameStartKey` and `CompactRangeDelsSameStartKey` exercise overlapping tombstones with the same lower bound. `CompactionRemovesCoveredKeys` and `CompactionRemovesCoveredMergeOperands` use ticker counts and `ignore_range_deletions` reads to prove compaction physically drops covered point keys or merge operands. `PutDeleteRangeMergeFlush` protects a sequence where a covered put must not reappear after merge processing.

File-boundary tests construct LSM layouts with fixed memtable factories, target file sizes, `max_compaction_bytes`, and manual level moves. They validate that tombstones spanning multiple output files do not create overlapping file ranges, that sentinel tombstones are omitted from physical outputs, that range tombstone end keys can be SST largest keys without corrupting overlap invariants, and that tombstones are written only to the minimal necessary SSTs. Related tests cover subcompactions, universal compaction, TTL-driven file cuts, SST partitioner cuts, oversized compaction gaps, overlapped tombstones, overlapped point keys, and non-bottommost compaction dropping only tombstones that do not overlap lower-level files and are not snapshot-protected.

Read-path tests verify coverage from every storage tier. `GetCoveredKeyFromMutableMemtable`, `GetCoveredKeyFromImmutableMemtable`, and `GetCoveredKeyFromSst` check point reads. `GetCoveredMergeOperandFromMemtable`, `KeyAtOverlappingEndpointReappears`, `UntruncatedTombstoneDoesNotDeleteNewerKey`, and `DeletedMergeOperandReappearsIterPrev` stress merge operands, overlapping endpoints, sequence-number zeroing, and forward/backward traversal modes. `GetIgnoresRangeDeletions` and `IteratorIgnoresRangeDeletions` ensure `ReadOptions::ignore_range_deletions` sees underlying keys in SST, immutable memtable, and mutable memtable.

Iterator tests cover normal snapshots, refresh, tailing unsupported status, reseek counters, sentinels, prefix seeks, upper bounds, file-read errors, and released snapshots. They build multi-level layouts with tombstones in memtable/L0/L1/L2/L3 and assert exact forward/backward key sequences for `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, and `Refresh(snapshot)`. Low-level tests use `LevelIterator` directly and expect sentinel keys at tombstone boundaries so covered lower-level keys are skipped even when a file has only tombstones or the seek target is outside point-key bounds.

Compensated-size tests verify `FileMetaData::compensated_range_deletion_size` during flush, compaction, and reopen. They compute lower-level file sizes with `Size()`, add tombstones covering those files, and assert the compensated size equals overlapped lower-level file sizes, is persisted through reopen, and is not double-counted when identical lower/upper bounds appear at different sequence numbers.

The final tests address edge cases. `SingleKeyFile`, `AddRangeDelsSameLowerAndUpperBound`, and `AddRangeDelsSingleUserKeyTombstoneOnlyFile` force compaction output cuts around multiple versions of one user key and around tombstone-only output so file smallest/largest keys remain valid. `MemtableMaxRangeDeletions` checks the dynamic option that causes flush when too many range tombstones accumulate. `RangeDelReseekAfterFileReadError` injects retryable IO errors and proves range-del reseek does not clear iterator error status. `ReleaseSnapshotAfterIteratorCreation` ensures iterators do not dereference `ReadOptions::snapshot` after construction, and `SeekForPrevTest` verifies user-visible reverse seeks after deleting the middle of a partitioned SST layout.

## State And Persistence Behavior
The suite treats range tombstones as durable, sequence-numbered records with half-open user-key bounds. Tombstones may live in mutable memtables, immutable memtables, L0, or deeper levels; flush and compaction decide whether to preserve, truncate, split, or drop them according to snapshots, bottommost status, lower-level overlap, and output file boundaries.

Snapshots are central state. Many tests hold snapshots to prevent tombstones or covered keys from being dropped during flush/compaction, then release them to permit sequence-number zeroing or obsolete-tombstone cleanup. Snapshot reads and iterator refresh with snapshot must see keys that were visible before a tombstone, even if newer live reads skip them.

Persistent file metadata is heavily asserted. Tests inspect `FileMetaData::smallest`, `largest`, `smallest_seqno`, table properties `num_range_deletions`, live file metadata, level file counts, and compensated range-deletion size. Reopen tests prove compensated sizes survive MANIFEST recovery. Meta-level invariants include non-overlapping files at a level, tombstone end keys used as upper bounds without overlap, and valid smallest/largest ordering even for tombstone-only or single-user-key output.

Read options can change visibility without rewriting state. `ignore_range_deletions` exposes covered keys/merge operands for verification; `iterate_upper_bound` must keep tombstones outside the bound from entering merging-iterator heaps; `read_tier=kMemtableTier` with iterator refresh must not double-free stale memtable tombstone iterators; tailing iterators reject range tombstones.

## Dependencies And Integration Points
This file depends on `db/db_test_util.h`, `db/version_set.h`, `rocksdb/utilities/write_batch_with_index.h`, test utility assertions, random generation, and merge operators. It also reaches into RocksDB internals through column-family handles, version/super-version level iterators, table cache eviction, internal key construction, manual compaction helpers, sync points, perf context, and file metadata inspection.

Integration points include block-based table-only range deletion support, row cache incompatibility, memtable factories and bloom filters, prefix extractors and Bloom filters, compaction picker/output splitting, `RangeDelAggregator`, `MergingIterator`, `LevelIterator` sentinel generation, `CompactionIterator`, merge operator semantics, snapshot stripe ordering, table property accounting, `SstPartitioner`, FIFO/TTL compaction, universal and leveled compaction, background flush/compaction scheduling, and filesystem read-error propagation.

## Risks
Range deletion correctness is high risk because the same tombstone must affect reads, iterators, compaction, metadata, and file boundaries consistently. Off-by-one errors on half-open bounds can delete the endpoint, fail to delete the start, or place tombstones in files whose key range does not actually overlap the tombstone.

Iterator direction changes are subtle. Several regressions involve using the wrong range-del positioning mode while scanning merge operands, sentinel keys remaining at heap tops, or reseek logic skipping too far. Tests check both user iterators and internal level iterators to catch these issues.

Compaction output splitting is another risk. Range tombstones can force or inhibit file cuts, add compensated size, span files, or create tombstone-only outputs. Incorrect handling can violate non-overlap invariants, double-count lower-level overlap, retain obsolete tombstones, or drop snapshot-protected tombstones.

The test suite is sensitive to internal names and layout heuristics. SyncPoint callbacks, exact file counts, manual compaction targets, target file sizes, and partitioner decisions are chosen to force specific internal paths; legitimate compaction behavior changes may require updating the tests while preserving the same invariants.

## Test Signals
Strong success signals include not-supported/invalid-argument status for unsupported APIs, exact not-found/found behavior for covered and uncovered keys, correct merge sums with and without `ignore_range_deletions`, expected ticker increments for keys/tombstones dropped by compaction, non-overlapping file metadata after compaction, and exact table-property range-deletion counts.

Iterator signals are especially valuable: expected forward and backward key sequences across snapshots and levels, `internal_range_del_reseek_count` increments only where tombstones force reseeks, tailing iterator not-supported status, refresh respecting snapshots across mutable/immutable/L0/L1 states, upper-bound tests avoiding tombstone heap processing, and injected IO errors remaining visible after range-del reseek.

Metadata and persistence signals include correct `compensated_range_deletion_size` during flush/compaction/reopen, no double-counting identical tombstone bounds, stable smallest/largest internal keys around tombstone sentinels, valid behavior for tombstone-only files/levels, dynamic `memtable_max_range_deletions` triggering flush, and row cache rejecting range deletion without leaving the DB read-only.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_range_del_test.cc -->

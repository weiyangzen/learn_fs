# sources/storage-engines/rocksdb/db/db_test.cc lines 1-7451

## Scope

This chunk covers the first 7,451 lines of RocksDB's broad `db_test.cc` GoogleTest file. It starts with test fixture setup for `DBTest` and `DBTestWithParam`, then exercises core DB behavior across environments, writes, reads, snapshots, metadata reporting, compaction styles, dynamic options, thread status, write stalls, WAL flushing, row cache, and `PinnableSlice` handling. The chunk ends inside `TEST_F(DBTest, ReusePinnableSlice)`, so the final `ReusePinnableSlice` expectations continue in a later chunk.

The file is test code in `ROCKSDB_NAMESPACE`, not production implementation. Its value is integration coverage: it drives public `rocksdb::DB` APIs plus internal `DBImpl` test hooks through `DBTestBase`, `SpecialEnv`, `SyncPoint`, mock time, background thread controls, and direct metadata inspection.

## Purpose

The primary purpose of this range is to validate high-level DB semantics and internal state transitions under many option configurations. It tests:

- DB open/reopen, destroy, mock env, mem env, and column family setup;
- request ID propagation from `ReadOptions` into filesystem `IODebugContext`;
- writes, empty batches, `WriteOptions::no_slowdown`, write queue behavior, WAL flush races, and large batches;
- reads from persisted tier, `Get`, iterator, `MultiGet`, prefix index fallback, total-order seek, and row-cache interactions;
- `SingleDelete`, `Delete`, snapshots, hidden-version cleanup, deletion marker elimination, and L0 ordering;
- metadata APIs for column family/file/blob metadata, live files, live file storage info, and live manifest size;
- approximate size and memtable stats APIs;
- custom comparators, table format option validation, checksum changes, rate limiter compatibility, and concurrent memtable support checks;
- multi-threaded atomic write/read validation across column families and randomized model-vs-real DB comparison;
- FIFO, TTL FIFO, universal, leveled, manual, automatic, and suggested compactions;
- dynamic mutable option changes for memtable, compaction, FIFO, universal, and miscellaneous options;
- thread tracking/status, shutdown cancellation behavior, background error handling, and write stall/delay conditions;
- cache lifetime behavior for row cache entries pinned through `PinnableSlice`.

## Important APIs, Types, And Functions

- `class DBTest : public DBTestBase` is the main fixture and disables fsync for speed through `DBTestBase("db_test", false)`.
- `class DBTestWithParam` adds `max_subcompactions_` and `exclusive_manual_compaction_` parameters for compaction tests.
- `MockEnvTest` and `MemEnvTest` validate basic open/put/get/iterator/flush/reopen behavior against `MockEnv` and `NewMemEnv`.
- `RequestIdPlumbingTest` uses `SyncPoint` callbacks in `RandomAccessFileReader::Read` and `MultiRead` to verify `ReadOptions::request_id` reaches `IODebugContext` and is copied safely.
- `SkipDelay`, `MixedSlowdownOptions`, `MixedSlowdownOptionsInQueue`, and `MixedSlowdownOptionsStop` exercise `WriteController` delay/stop tokens, `WriteOptions::no_slowdown`, writer queueing, and wakeup behavior.
- `ReadFromPersistedTier` validates `ReadOptions::read_tier = kPersistedTier` for `Get` and both `MultiGet` forms under WAL-enabled and WAL-disabled writes.
- Single delete and deletion-marker tests include `PutSingleDeleteGet`, `SingleDeleteFlush`, `SingleDeletePutFlush`, `UnremovableSingleDelete`, `DeletionMarkers1`, and `DeletionMarkers2`.
- Metadata helpers `CheckColumnFamilyMeta`, `CheckLiveFilesMeta`, `AddBlobFile`, and `CheckBlobMetaData` compare public metadata structs with internal `FileMetaData`, `VersionStorageInfo`, blob metadata, file numbers, keys, times, and path fields.
- `MetaDataTest`, `GetColumnFamilyMetaData*`, `AllMetaDataTest`, `SnapshotFiles`, `ReadonlyDBGetLiveManifestSize`, and `GetLiveBlobFiles` cover metadata and live-file APIs.
- Compression helpers `MinLevelHelper` and `MinLevelToCompress` configure per-level compression tests and skip when no compression backend is available.
- Approximation tests exercise `DB::GetApproximateSizes`, `SizeApproximationOptions`, `files_size_error_margin`, and `DB::GetApproximateMemTableStats`.
- `Snapshot` validates snapshot sequence/time tracking through raw snapshots and `ManagedSnapshot`.
- `ComparatorCheck` and `CustomComparator` validate comparator compatibility and a numeric comparator's behavior across compaction.
- Multi-threaded helpers `MTState`, `MTThread`, `MTThreadBody`, and `MultiThreadedDBTest` stress atomic cross-column-family writes using `WriteBatch`, `WriteBatchWithIndex`, and both vector and batched `MultiGet`.
- `ModelDB`, `ModelSnapshot`, `ModelIter`, `RandomKey`, `CompareIterators`, and `DBTestRandomized` implement an in-memory reference DB for randomized put/delete/batch/iterator/snapshot comparison.
- Prefix/index tests cover `BlockBasedTableOptions::kHashSearch`, prefix extractor changes via `SetOptions`, `Iterator::Refresh`, and total-order seek.
- FIFO tests include `FIFOCompactionTest`, `FIFOCompactionTestWithCompaction`, `FIFOCompactionStyleWithCompactionAndDelete`, and TTL/table-format compatibility variants.
- Dynamic option tests cover `SetOptions`, `TEST_GetLatestMutableCFOptions`, `MutableCFOptions`, `compaction_options_fifo`, `compaction_options_universal`, and `max_sequential_skip_in_iterations`.
- Thread status tests use `Env::GetThreadList`, `ThreadStatusUpdater`, `ThreadStatus::OP_FLUSH`, `ThreadStatus::OP_COMPACTION`, and DB properties `kNumRunningFlushes`/`kNumRunningCompactions`.
- Write stall tests use `WriteStallListener`, `WriteController`, soft/hard pending compaction byte limits, delayed write rate, and background task blocking.
- Row cache tests use `LRUCacheOptions`, `NewLRUCache`, `CacheWrapper`, `ROW_CACHE_HIT`, `ROW_CACHE_MISS`, and `PinnableSlice`.

## Control Flow

Most tests follow a common fixture-driven flow: configure an `Options` object, open or reopen a DB using `DBTestBase` helpers, create optional column families, perform writes/flushes/compactions, then assert public reads and internal counters. `ChangeOptions()`, `ChangeCompactOptions()`, and `CurrentOptions()` expand the same semantic test over multiple RocksDB table/compaction/memtable configurations while skip masks exclude unsupported combinations such as FIFO, universal compaction, plain table, hash index, or no-snapshot modes.

Environment tests open databases against mock or memory environments, write a few keys, verify direct reads and iterator order, force a memtable flush through `DBImpl::TEST_FlushMemTable()`, and reopen when persistence is expected. The request ID test installs sync callbacks around file reads, forces SST reads by flushing data, then checks that `Get`, iterator seek, and `MultiGet` supply the same request string through an `IODebugContext` copy rather than retaining the same pointer.

Write throttle tests create delay or stop tokens in `TEST_write_controler()`, then mix foreground writes with threads whose `WriteOptions::no_slowdown` is either true or false. Sync points pause inside delay/wait code paths so additional writers can enter queues. The assertions distinguish writes that should fail fast with no slowdown from writes that may block until the token is released or background CV is signaled.

Read tier tests deliberately alternate WAL-enabled and `disableWAL` writes. With `kPersistedTier`, unflushed data is visible only when it is recoverable from WAL; WAL-disabled, unflushed data must be invisible until flushed. The same logic is checked through ordinary `Get`, vector `MultiGet`, and batched `MultiGet` into `PinnableSlice`s.

Metadata tests manufacture SSTs with deterministic key ranges and injected blob references, inspect internal file metadata with `TEST_GetFilesMetaData`, then compare public `ColumnFamilyMetaData`, `LiveFileMetaData`, `BlobMetaData`, and `LiveFileStorageInfo` fields. They also cover key-range and level-filtered metadata queries, empty DB behavior, all-column-family metadata, blob-file path normalization, and manifest-size reporting in read-only mode.

Snapshot and deletion tests build version stacks with puts, deletes, single deletes, snapshots, flushes, and compactions. They verify when hidden values remain because snapshots pin them, when compaction can remove them, when `SingleDelete` must remain uncollapsed to preserve future delete semantics, and when deletion markers are removed only at the base level or after overlapping lower-level files are compacted.

The multi-threaded test creates ten column families and ten worker threads. Each writer stores values encoding key, writer id, operation counter, column-family id, and a random unique id across all CFs in a single batch. Readers use `MultiGet` and assert all CFs agree on found/not-found status and unique id, proving cross-CF atomicity under concurrent reads and writes.

The randomized test drives a real DB and `ModelDB` through 10,000 random operations. It periodically compares iterators with and without saved snapshots, reopens the real DB, releases old snapshots, and saves new model/real snapshots. This makes persistence, iterator ordering, and snapshot isolation match a simple ordered-map reference for option configurations that support the required iterator semantics.

Compaction tests construct LSM states with controlled file ranges and sizes, then trigger automatic, manual, FIFO, TTL, universal, suggested, promoted, and compact-files paths. They use `Flush`, `MoveFilesToLevel`, `TEST_CompactRange`, `CompactRange`, `CompactFiles`, and `experimental::SuggestCompactRange`/`PromoteL0` to assert file counts, deleted keys, unsupported combinations, compaction-filter context, conflict detection, and concurrent flush allowance.

Dynamic option tests first establish a baseline LSM or memtable state, call `SetOptions()` with string-encoded option changes, force flush/compaction boundaries so new mutable options are active, and assert both visible behavior and `MutableCFOptions` values. The options include write buffer size/count, L0 triggers, file size/base/multiplier settings, disabling auto compaction, FIFO/TTL fields, universal compaction fields, compression, paranoid file checks, report-bg-io stats, and iteration reseek threshold.

Thread-status tests use sync points to hold flushes or compactions in-progress, then query `Env::GetThreadList()` and DB running-operation properties. Shutdown tests cancel background work before manual compaction or flush and assert `ShutdownInProgress`, no active compaction operation remains, and destruction can proceed with WAL-disabled data.

Write stall tests block background compaction or flush work with `SleepingBackgroundTask`, generate L0 and lower-level files to exceed soft or hard pending compaction limits, and observe `WriteController` delay/stop state plus `WriteStallListener` notifications. Mock time is used for delayed write rate estimation, merge/filter operation timing, TTL FIFO expiry, and snapshot timestamp checks.

Row cache tests write and flush a key, observe cache miss/hit counters across reads, wrap row cache insertion to simulate `MemoryLimit`, and verify cache entry lifetime when a read returns a `PinnableSlice`. The chunk ends while extending the same pinned-lifetime checks to repeated `Get` and `MultiGet` calls.

## State And Persistence Behavior

- Tests repeatedly exercise durable state transitions: memtables become immutable, flushes create SSTs, compactions rewrite levels, MANIFEST state survives reopen, and WAL state determines persisted-tier visibility.
- `WriteEmptyBatch` confirms an empty synced write batch does not corrupt WAL/reopen behavior with column families.
- Reopen tests validate option compatibility with on-disk state, including number-of-levels constraints and comparator names.
- Snapshot tests depend on sequence-number and snapshot-time bookkeeping: `GetNumSnapshots`, `GetTimeOldestSnapshots`, and `GetSequenceOldestSnapshots` must update as snapshots are acquired and released.
- Single-delete and deletion-marker tests assert that compaction preserves or drops internal keys based on snapshot visibility, base-level status, and single-delete correctness.
- Metadata tests compare durable SST/blob metadata fields, including file number, size, smallest/largest seqno, smallest/largest user key, creation time, oldest ancestor time, epoch number, blob checksums, and path decomposition.
- `SnapshotFiles` disables file deletions, copies live files including a trimmed MANIFEST snapshot, opens the copy as a second DB, then validates copied contents. It also checks live-file storage info after closing with file deletions disabled.
- FIFO/TTL compaction tests use mock time to show expired files are not removed merely because time passes; a manual or automatic compaction trigger must run.
- Dynamic option tests show mutable options are not purely config storage: they affect future memtable sizes, L0 write stops, compaction output sizing, and SuperVersion-visible prefix extractor behavior.
- WAL concurrency tests (`ConcurrentFlushWAL`, `ManualFlushWalAndWriteRace`) verify concurrent `Put`, internal two-queue writes, `FlushWAL`, synced writes, and reopen recovery do not lose or corrupt data.
- File-creation random failure injects `SpecialEnv::non_writeable_rate_`, expects flush/compaction I/O errors, preserves latest successful updates in memory, then reopens after clearing failures and revalidates data.
- Row cache tests mutate cache state without changing DB contents: cache entries are removed from the LRU while pinned by `PinnableSlice` and returned when the slice is destroyed.

## Dependencies And Integration Points

- The test fixture depends heavily on `db/db_test_util.h` for helpers such as `Put`, `Get`, `Flush`, `Compact`, `MoveFilesToLevel`, `FilesPerLevel`, `GenerateNewFile`, `GenerateNewRandomFile`, `Reopen`, `DestroyAndReopen`, `CreateAndReopenWithCF`, `TryReopenWithColumnFamilies`, and internal `dbfull()` access.
- Internal DB integration points include `DBImpl`, `VersionSet`, `VersionStorageInfo`, `ColumnFamilyData`, `ColumnFamilyHandleImpl`, `WriteBatchInternal`, `JobContext`, `ThreadStatusUtil`, table cache test hooks, and `DBImpl` test-only methods.
- Public RocksDB APIs covered include `DB::Open`, `Put`, `Delete`, `SingleDelete`, `Merge`, `Write`, `Get`, `MultiGet`, `NewIterator`, `GetSnapshot`, `ReleaseSnapshot`, `Flush`, `FlushWAL`, `CompactRange`, `CompactFiles`, `SetOptions`, `GetOptions`, `GetIntProperty`, `GetColumnFamilyMetaData`, `GetAllColumnFamilyMetaData`, `GetLiveFiles`, `GetLiveFilesMetaData`, `GetLiveFilesStorageInfo`, and `DestroyDB`.
- Table-format integration includes block-based table factories, hash and binary index modes, plain/adaptive table checks, bloom filters, checksum types, prefix extractors, and table property collection.
- Compaction integration spans leveled, universal, FIFO, TTL FIFO, manual exclusive compaction, suggested compaction, `PromoteL0`, compaction filters/factories, merge operators, background compaction scheduling, and stall conditions.
- Environment integration includes `MockEnv`, `NewMemEnv`, `SpecialEnv` behavior in the fixture, mock sleep/time, filesystem path creation/deletion/copying, background thread pools, random file creation failure, and live file-size checks.
- Concurrency integration uses `port::Thread`, `Env::StartThread`, `Env::WaitForJoin`, background task sleepers, atomics, `MutexLock`, condition variables, and `SyncPoint` dependencies/callbacks.
- Statistics integration includes tickers and histograms such as `WRITE_DONE_BY_OTHER`, `DB_WRITE`, `MERGE_OPERATION_TOTAL_TIME`, `FILTER_OPERATION_TOTAL_TIME`, `COMPACTION_CPU_TOTAL_TIME`, `GET_HIT_L0`, `GET_HIT_L1`, `GET_HIT_L2_AND_UP`, `ROW_CACHE_HIT`, `ROW_CACHE_MISS`, `NUMBER_OF_RESEEKS_IN_ITERATION`, and `FLUSH_WRITE_BYTES`.
- External utility integration includes `Checkpoint`-style live file snapshotting concepts, `WriteBatchWithIndex`, `OptimisticTransactionDB` includes for shared test compilation context, merge operators, cache wrappers, rate limiter implementations, and compression feature probes.

## Risks And Edge Cases

- Many tests are timing or scheduling sensitive. They mitigate this with `SyncPoint`, mock sleep, and blocking background tasks, but comments still flag potential flakiness in delay/write-stall and thread-status paths.
- Option iteration through `ChangeOptions()` can mask a bug if the skip policy is too broad or a feature is unsupported by a table format. The tests must preserve accurate skip masks for FIFO, universal, plain table, hash index, no snapshot, and no seek-to-last configurations.
- Request ID plumbing depends on copied `IODebugContext` retaining the pointed-to string value without aliasing the original pointer. Future refactors in file readers could bypass the tested sync points.
- `kPersistedTier` behavior differs with WAL disabled. Reads that accidentally consult mutable memtables or ignore WAL persistence would break the intended matrix.
- Single-delete compaction is especially delicate: incorrectly removing an unremovable single delete can make a later `SingleDelete` reveal an older value.
- Metadata validation assumes public metadata order matches internal `files_by_level` order. Changes in ordering semantics would require adjusting `CheckLiveFilesMeta` rather than weakening field checks.
- Snapshot file copying trims the MANIFEST to the reported valid size. Manifest-size regressions can cause copied snapshots to include invalid tail data or miss necessary edits.
- Multi-threaded and randomized tests are broad bug detectors but expensive; the randomized test is excluded for normal valgrind unless full valgrind is requested.
- FIFO TTL support is constrained to `max_open_files == -1` and block-based tables. Relaxing either constraint without updating tests risks silent unsupported combinations.
- Dynamic mutable options often require a new memtable, flush, compaction, iterator refresh, or SuperVersion to become visible. Tests document these activation boundaries and can fail if a change takes effect too early or too late.
- Thread status tests can be flaky if compactions finish before inspection; they use sync points but still include comments about known fragility.
- Write stall notification tests depend on event listener timing after flush context cleanup; they install a custom wait around `DBImpl::BackgroundCallFlush:ContextCleanedUp` to avoid observing stale listener state.
- File-creation random failure leaves the DB in an I/O-error state until the injected failure is cleared. The test expects latest successful writes only, not all attempted writes.
- Row cache tests downcast to `LRUCache` and inspect `TEST_GetLRUSize`, so they depend on current row-cache implementation details and aliasing among `RowCache`, `BlockCache`, and `Cache`.

## Test Signals

- Basic environment tests signal success through ordered iterator output, flushed reads, and mem-env reopen visibility.
- Request ID plumbing signals success when read and multiread sync callbacks observe the exact request string and copied `IODebugContext` owns a distinct request pointer.
- Write throttle tests signal correct behavior through `ASSERT_NOK` for no-slowdown writes under delay/stop and `ASSERT_OK` for blocking writes after tokens are released.
- Persisted-tier tests signal correct WAL semantics by comparing unflushed, flushed, and deleted keys across both `Get` and `MultiGet`.
- Metadata tests signal correctness by matching public metadata to internal file/blob metadata field-by-field and by filtering key ranges/levels to expected file counts.
- Approximate-size tests use bounded ranges rather than exact sizes where format overhead varies, while memtable stats tests use deterministic seeds and exact expected counts/sizes.
- Snapshot tests signal correct sequence/time tracking and isolation through old values returned under snapshots and updated oldest snapshot metadata after releases.
- Deletion and compaction tests use `AllEntriesFor`, `FilesPerLevel`, `NumTableFilesAtLevel`, and `Get` to check internal-key retention and visible values.
- Comparator tests require reopen failure on comparator mismatch and correct equivalence of decimal/hex numeric keys under a custom comparator.
- Multi-threaded tests signal atomic cross-CF writes when all read values share status and unique id.
- Randomized tests signal broad correctness when model and real iterators agree across operations, reopen, and snapshots.
- Prefix/index tests signal fallback and dynamic SuperVersion correctness when reads work after changing prefix extractors and after forcing table cache eviction.
- FIFO/TTL tests signal compaction correctness with file counts, size limits, and deleted key ranges after manual or automatic compaction.
- Dynamic option tests signal live option application through changed file counts/sizes, `MutableCFOptions` values, stall thresholds, reseek ticker counts, and disabled/enabled compaction behavior.
- Thread-status tests signal operation tracking through `Env::GetThreadList` counts and DB running flush/compaction properties while sync points hold work in progress.
- Timing/stat tests signal accounting correctness through merge/filter/compaction elapsed-time tickers and histograms after mock sleeps or CPU-time recording.
- Write stall tests signal delay/normal transitions through `TEST_write_controler().NeedsDelay()`, `IsStopped()`, listener state, and estimated mock elapsed time.
- Row cache tests signal cache behavior through row-cache hit/miss tickers, insertion-failure misses, and LRU size changes while values are pinned.

## Unresolved Cross-Chunk References

- The file continues after line 7,451 with the remainder of `ReusePinnableSlice`, old-WAL deletion after column-family drop, unsupported manual sync, parameter instantiation, open-files-async tests, and `main()`. The final per-file synthesis should merge those later test clusters with this chunk.
- `DBTestBase` helpers, option-config enums, `SpecialEnv`, `FlushCounterListener`, `VerifySstUniqueIds`, and many `TEST_*` hooks are defined outside this file or outside this chunk; this report describes their use here rather than their implementations.
- Some tests in this chunk are disabled (`DISABLED_*`) or gated by platform/preprocessor symbols such as `OS_WIN`, `ROCKSDB_VALGRIND_RUN`, `NROCKSDB_THREAD_STATUS`, and `ROCKSDB_DISABLE_STALL_NOTIFICATION`; later reconciliation should preserve these guards when summarizing executable test coverage.

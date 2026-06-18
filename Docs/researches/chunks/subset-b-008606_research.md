# sources/storage-engines/rocksdb/db/db_test.cc lines 7452-8434

## Scope

This chunk covers the final tests in `db_test.cc`, starting at the tail of a row-cache `MultiGet` assertion and continuing through standalone `DBTest` cases for WAL deletion, manual WAL sync capability, paused background work, thread-local iterator cleanup, block-based table option validation, file creation time, write-buffer memory retention, stalled writes during shutdown, sampled file-read counters, collapsible-entry sampled counters, and the parameterized `OpenFilesAsyncTest` suite. It ends with namespace closure and the GoogleTest `main()`.

The code is test-only but exercises production APIs across DB open/reopen, column families, WAL management, background work scheduling, table cache lookup, file metadata, async table reader opening, read-only opens, corruption propagation, and SyncPoint-controlled races.

## Purpose

The tests in this range verify that RocksDB preserves correctness around late-lifecycle and concurrency-sensitive DB behavior:

- Dropping a column family while its old WAL is being flushed should not prevent WAL rotation and cleanup decisions from progressing.
- `DB::SyncWAL()` must report `NotSupported` when the environment declares WAL sync as not thread-safe.
- `PauseBackgroundWork()` should apply enough backpressure that a write-heavy thread cannot finish until `ContinueBackgroundWork()` resumes work.
- Destroying many short-lived iterator threads while another thread repeatedly flushes should not deadlock thread-local pointer cleanup.
- Invalid huge block-based table block sizes should prevent DB reopen instead of silently accepting unusable options.
- `GetCreationTimeOfOldestFile()` should return the oldest known SST creation time, preserve zero as an "unknown/oldest" sentinel, and reject configurations where table readers are not pinned.
- `max_write_buffer_size_to_maintain` should bound retained immutable memtable memory after flushes.
- DB shutdown should unblock writes stalled by L0 stop triggers with `Status::kShutdownInProgress`.
- Sampled file-read counters and sampled collapsible-entry counters should update through `Get`, `MultiGet`, iterator, L0, and non-L0 table access paths.
- Async file opening at DB open should race safely with reads, compactions, shutdown, corrupt files, dropped column families, and creation-time lookup.

## Important APIs, Types, And Functions

- `TEST_F(DBTest, DeletingOldWalAfterDrop)` configures small `max_total_wal_size`, disabled compactions, huge L0 thresholds, creates two extra column families, drops the default handle while a flush is synchronized, and checks `DBImpl::TEST_LogfileNumber()` advances after later writes to another CF.
- `TEST_F(DBTest, UnsupportedManualSync)` mutates the test environment flag `env_->is_wal_sync_thread_safe_` and verifies `db_->SyncWAL()` returns `Status::NotSupported`.
- `TEST_F(DBTest, PauseBackgroundWorkTest)` uses `db_->PauseBackgroundWork()`, a writer `port::Thread`, an atomic `done`, and `db_->ContinueBackgroundWork()` to test stalled/resumed background work.
- `TEST_F(DBTest, ThreadLocalPtrDeadlock)` concurrently creates/destroys short-lived iterator threads and repeatedly calls `DB::Flush()` to exercise thread-local cleanup interactions.
- `TEST_F(DBTest, LargeBlockSizeTest)` builds `BlockBasedTableOptions` with an 8 GiB block size through `NewBlockBasedTableFactory()` and expects reopen failure.
- `TEST_F(DBTest, CreationTimeOfOldestFile)` uses mock time, `PropertyBlockBuilder::AddTableProperty:Start`, `FileMetaData::FileMetaData`, `TableProperties::file_creation_time`, `FileMetaData::file_creation_time`, and `dbfull()->GetCreationTimeOfOldestFile()`.
- `TEST_F(DBTest, MemoryUsageWithMaxWriteBufferSizeToMaintain)` reaches through `ColumnFamilyHandleImpl` to `ColumnFamilyData`, then samples `mem()->ApproximateMemoryUsage()` and `imm()->ApproximateMemoryUsage()`.
- `TEST_F(DBTest, ShuttingDownNotBlockStalledWrites)` combines L0 stop triggers, delayed background compaction, `DBImpl::DelayWrite:Wait`, `CancelAllBackgroundWork()`, and expected `Status::kShutdownInProgress`.
- `TEST_F(DBTest, FileReadSampledStats)` and `TEST_F(DBTest, FileCollapsibleEntryReadSampledStats)` force `should_sample_file_read`, access `FileMetaData::stats.num_reads_sampled` and `num_collapsible_entry_reads_sampled`, and validate increments by `kFileReadSampleRate`.
- `enum class ReadType` enumerates `kGet`, `kMultiGet`, and `kIterator` read paths for the async-open suite.
- `class OpenFilesAsyncTest` derives from `DBTest` and `testing::WithParamInterface<std::tuple<uint32_t, int, bool>>`; its parameters are `num_flushes_`, `max_open_files_`, and `read_only_`.
- `OpenFilesAsyncTest::SetupData()` creates a DB with disabled auto compactions, optional CFs, one flushed SST per parameterized flush per CF, then closes it.
- `OpenFilesAsyncTest::VerifyData()` reads all generated keys through `Get`, `DB::MultiGet()`, or an `Iterator`.
- `OpenFilesAsyncTest::OpenTestDB()` enables `options.open_files_async`, `skip_stats_update_on_db_open`, and statistics, lists CFs, then reopens read-write or read-only.
- `OpenFilesAsyncTest::VerifyReadError()` asserts corruption is surfaced through each read API.
- Parameterized tests `ConcurrentFileAccess`, `AfterRead`, `BeforeRead`, `GetCreationTimeOfOldestFileSkipsWaitForModernDB`, `GetCreationTimeOfOldestFileBlocksOnAsyncOpenForLegacyDB`, `Shutdown`, `Error`, and `DropColumnFamily` cover async table reader opening order and failure modes.

## Control Flow

The chunk begins by completing a row-cache `MultiGet` scenario: after a pinned value lookup, the test expects the row-cache LRU size to drop to zero while the `PinnableSlice` owns the entry and return to one after destruction.

`DeletingOldWalAfterDrop` uses SyncPoint dependencies so a flush can be held while a column family is dropped. Large writes force WAL pressure under a tiny `max_total_wal_size`; the dropped CF makes the synchronized flush a no-op. The test then writes to another CF and expects a newer WAL number, proving dropped-CF flush state does not strand obsolete WAL lifecycle state.

The following standalone DB tests each set up a focused invariant. `UnsupportedManualSync` reopens with default options, flips the mock environment support flag, and directly checks `SyncWAL()`. `PauseBackgroundWorkTest` starts with background work paused, launches a thread doing 10,000 random puts, sleeps long enough to observe it has not completed, resumes background work, joins, and confirms completion. `ThreadLocalPtrDeadlock` runs one flushing thread until more than ten flushes have completed while ten spawner threads continuously create a nested short-lived thread that allocates and deletes an iterator.

`CreationTimeOfOldestFile` manipulates both table properties and manifest `FileMetaData` through SyncPoint callbacks. The first pass alternates one SST with zero `file_creation_time` and one with `uint_time_1`, while the manifest metadata is forced to zero; `GetCreationTimeOfOldestFile()` must return zero. The second pass uses `uint_time_1` and `uint_time_2`, expecting `uint_time_1` as oldest. A final reopen with `max_open_files = 10` verifies the API is unsupported without pinned table readers.

`MemoryUsageWithMaxWriteBufferSizeToMaintain` repeatedly writes 1 KiB values, waits for flushes, and watches active plus immutable memtable memory. It allows a single iteration to exceed the configured retention plus write-buffer size, but asserts the condition cannot persist across the next write.

`ShuttingDownNotBlockStalledWrites` first creates 20 L0 files with auto compactions disabled. It then reopens with compactions enabled and `level0_stop_writes_trigger = 20` so a new write stalls. SyncPoints hold compaction long enough for `CancelAllBackgroundWork(db_.get(), true)` to set shutdown state, and the blocked writer must return `kShutdownInProgress`.

`FileReadSampledStats` and `FileCollapsibleEntryReadSampledStats` force sampling on every file read. They create SSTs in L1 and L0, reset atomic counters directly on `FileMetaData`, and confirm `Get` and iterator access increment read counters while missing-key probes, deletes, and merge operands increment collapsible-entry counters only where expected.

The async-open fixture writes deterministic key/value pairs into flushed files, closes the DB, then reopens with `open_files_async = true`. Each parameterized test loops over all read APIs. `ConcurrentFileAccess` runs reads concurrently with a manual compaction. `AfterRead` arranges the first foreground read to occur before background async open finds tables, so pinned readers should be absent at read time and populated later by `BGWorkAsyncFileOpen`. `BeforeRead` waits for async open before the read and expects pinned readers to already exist when `max_open_files == -1`.

The creation-time async-open tests split modern and legacy behavior. Modern DB metadata should let `GetCreationTimeOfOldestFile()` return without entering `WaitForAsyncFileOpen()`. The legacy simulation forces unknown file creation times until `BGWorkAsyncFileOpen:Done`; the caller thread must block in `WaitForAsyncFileOpen`, then complete after the main thread releases the async opener.

The remaining async-open tests cover shutdown, corruption, and dropped CF handling. `Shutdown` closes the DB while async open is delayed and checks no file opens occur before destructor wait. `Error` corrupts all SSTs, opens with async file open, waits for background completion, checks `TEST_GetBGError()` is corruption, and verifies each read path reports corruption. `DropColumnFamily` delays async open, drops and destroys a non-default CF handle, releases async open, and verifies default-CF reads remain correct.

## State And Persistence Behavior

- The tests repeatedly create durable state through `Put`, `Delete`, `Merge`, `Flush`, `MoveFilesToLevel`, and reopen/close cycles. The expected observations come from persisted WALs, MANIFEST entries, SST properties, and table metadata rather than transient in-memory writes alone.
- WAL lifecycle state is tested by comparing `TEST_LogfileNumber()` before and after writes that follow a dropped CF and synchronized no-op flush.
- File creation time has two sources in these tests: table properties (`TableProperties::file_creation_time`) and manifest metadata (`FileMetaData::file_creation_time`). The zero value is treated as an unknown/oldest sentinel, while nonzero values are compared for oldest-file selection.
- `max_open_files == -1` is central: table readers can be pinned in `FileDescriptor::pinned_reader`, enabling async open and creation-time lookup. With bounded `max_open_files`, the creation-time API returns `NotSupported` and file-open ticker expectations become lower-bound checks.
- Async file opening mutates in-memory table-reader state after DB open. The tests deliberately distinguish foreground reads that can open tables from background `BGWorkAsyncFileOpen` work that pins readers later.
- Background errors from async table open are stored in DB state and visible through `TEST_GetBGError()`, while read APIs still independently surface corruption when accessing damaged SSTs.
- `PauseBackgroundWork()` and `CancelAllBackgroundWork()` alter scheduler/shutdown state rather than persisted data; tests confirm their visible effect on write progress and stalled-write return status.
- Sampled stats live in `FileMetaData::stats` atomics. The tests reset and inspect counters directly, so they validate metadata-side accounting rather than public statistics aggregation alone.

## Dependencies And Integration Points

- GoogleTest macros and parameterization (`TEST_F`, `TEST_P`, `INSTANTIATE_TEST_CASE_P`, `ASSERT_OK`, `ASSERT_EQ`, `EXPECT_GE`) provide the execution harness.
- `DBTest` helper APIs supply `CurrentOptions()`, `DestroyAndReopen()`, `Reopen()`, `TryReopenWithColumnFamilies()`, `TryReopenReadOnlyWithColumnFamilies()`, `CreateColumnFamilies()`, `CreateAndReopenWithCF()`, `Put()`, `Get()`, `Delete()`, `Flush()`, `MoveFilesToLevel()`, `GetLevelFileMetadatas()`, `GetSstFileCount()`, `Close()`, and `dbfull()`.
- SyncPoint names connect these tests to production code in `DBImpl`, `VersionBuilder`, `Version`, `TableCache`, `PropertyBlockBuilder`, `FileMetaData`, and file-read sampling logic.
- The table/cache layer is exercised through `TableCache::Get`, `TableCache::MultiGet`, `TableCache::NewIterator`, `FileDescriptor::pinned_reader`, `FileMetaData`, and table property builders.
- Column-family integration appears through `CreateColumnFamilies`, `DropColumnFamily`, `DestroyColumnFamilyHandle`, `ColumnFamilyHandleImpl`, `ColumnFamilyData`, and read/write helper overloads taking CF indexes.
- Background scheduling integration includes flush workers, compaction workers, async file-open workers, `PauseBackgroundWork`, `ContinueBackgroundWork`, write stalling, and `CancelAllBackgroundWork`.
- Storage error handling is tested through `test::CorruptFile`, `GetLiveFilesMetaData`, async background error state, and corruption propagation in `Get`, `MultiGet`, and iterator status.
- The final `main()` installs RocksDB's stack trace handler, initializes GoogleTest, registers custom objects, and runs all tests.

## Risks And Edge Cases

- SyncPoint ordering is essential. If production sync point names change or a dependency is incomplete, tests can become nondeterministic or stop covering the intended race.
- Async file open behavior differs sharply between `max_open_files == -1` and bounded file caches. Several assertions intentionally become exact only for pinned-reader mode.
- `CreationTimeOfOldestFile` forces manifest metadata to zero while table properties vary. This simulates legacy/partial metadata behavior but depends on callbacks firing for the expected files and in the expected alternating order.
- The memory-retention test uses approximate memory accounting and repeated flush waits. It allows one transient overshoot to avoid false positives but would catch a retained-memory leak that does not drop on subsequent writes.
- `PauseBackgroundWorkTest` relies on elapsed sleep and a large write count to prove the writer is blocked; on unusual scheduling or option behavior, timing sensitivity could matter.
- `ThreadLocalPtrDeadlock` is a liveness regression test. It does not assert a data result, so its signal is primarily "test completes without deadlock."
- The read-sampling tests reset counters that may have been touched by compaction or setup. Missing a setup-side increment would make assertions flaky unless counters are reset immediately before the read path under test.
- The collapsible-entry counter expectations rely on exactly one delete tombstone and one merge operand in the relevant SST. Compaction, merge-operator behavior, or iterator filtering changes could alter that count.
- `OpenFilesAsyncTest::Error` corrupts the first 100 bytes of every SST and expects corruption on all three read paths after background async open. If corruption detection becomes lazier, this test may need tighter read forcing.
- `DropColumnFamily` must destroy and null the dropped handle before default-CF reads. Any async opener use-after-drop would show up as crash, corruption, or incorrect open-count behavior.

## Test Signals

- Exact assertions on `Status` include `NotSupported` for unsupported WAL sync and bounded-file-cache creation-time lookup, `kShutdownInProgress` for writes unblocked by shutdown, and `Corruption` for async-open damaged SST reads.
- WAL rotation is signaled by `EXPECT_GT(lognum2, lognum1)` after writes following a dropped-CF flush.
- Background pause/resume is signaled by `done == false` during pause and `done == true` after continuation and thread join.
- Thread-local iterator cleanup is signaled by completion after more than ten flushes while many nested iterator threads were created and destroyed.
- Invalid table option handling is signaled by `ASSERT_NOK(TryReopenWithColumnFamilies(...))` with an 8 GiB block size.
- Creation-time correctness is signaled by returning zero when any oldest metadata is unknown, returning `uint_time_1` when all times are nonzero, skipping async-open wait for modern metadata, and blocking until async open for simulated legacy metadata.
- File-read sampling is signaled by `num_reads_sampled == kFileReadSampleRate` for L1 `Get`, L1 iterator, and L0 `Get`.
- Collapsible-entry sampling is signaled by zero counter increments for found values, one sample-rate increment for missing-key probes in a file range, and `2 * kFileReadSampleRate` for iterator exposure to one delete and one merge operand.
- Async file-open races are signaled by `NO_FILE_OPENS` ticker counts, `pinned_reader` null/non-null assertions at table-cache sync points, successful reads across all read types, and absence of file opens when shutdown wins before async open starts.

## Unresolved Cross-Chunk References

This chunk depends heavily on `DBTest` fixture helpers, mock `Env` fields, SyncPoint names, table cache internals, and DB implementation test hooks defined earlier in `db_test.cc` or in RocksDB test utilities. The final per-file research should reconcile this chunk with earlier row-cache tests before line 7452, the definitions of `DBTest` and `DBTestWithParam`, and production implementations for `DBImpl::GetCreationTimeOfOldestFile`, `DBImpl::BGWorkAsyncFileOpen`, file-read sampling, stalled-write delay, and WAL cleanup after dropped column families.

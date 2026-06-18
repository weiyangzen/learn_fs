# sources/storage-engines/rocksdb/db/db_compaction_test.cc lines 1-7097

## Purpose

This chunk contains the first half of RocksDB's `db_compaction_test.cc`, focused on exercising compaction correctness, scheduling, metadata accounting, output placement, and option interactions. It is test code, but it documents many contracts that production compaction code must preserve:

- tombstones and range tombstones must not resurrect older values across L0/L1+ file boundaries;
- manual, automatic, bottom-priority, intra-L0, TTL, periodic, and deletion-triggered compactions must pick safe input/output ranges;
- compaction scheduling must respect write-stall avoidance, background thread pools, conflict cancellation, task limiters, and exclusive manual compaction;
- table readers, direct I/O reader bypass, block cache behavior, file metadata, and event listener callbacks must remain consistent before, during, and after compaction;
- on-disk SST placement must obey `db_paths`, `cf_paths`, `target_path_id`, and compaction output-level rules across reopen.

The mapped range ends inside `UseDirectIoForCompactionReadsLevelIteratorWithTombstones`; the rest of that test and later compaction cases are outside this chunk and belong to later research chunks.

## Important Fixtures, Helpers, and Types

- `CompactionStatsCollector` is an `EventListener` that records counts by `CompactionReason` from compaction, flush, and external SST ingestion callbacks. `DBCompactionTest::VerifyCompactionStats()` compares listener-derived counts with `InternalStats::TEST_GetCompactionStats()` in debug builds.
- `DeletionTriggeredCompactionWithMinFileSizeTestListener` asserts that files selected for `kFilesMarkedForCompaction` satisfy a configured minimum file size by resolving SST names with `TableFileName()` and checking `Env::GetFileSize()`.
- `DBCompactionTest` derives from `DBTestBase` and resets `Env::Default()` LOW/HIGH/BOTTOM thread-pool sizes in `TearDown()` to avoid test cross-contamination.
- `DBCompactionTestWithParam` parameterizes tests by `(max_subcompactions, exclusive_manual_compaction)`. Its nested `TrivialMoveEventListener` asserts the `CompactionJobInfo::stats.num_input_files_trivially_moved` count observed at compaction begin.
- `DBCompactionWaitForCompactTest` parameterizes `WaitForCompactOptions` by `abort_on_pause`, `flush`, `close_db`, and `timeout`, and builds a DB state one L0 file short of an automatic compaction trigger.
- `DBDeleteFileRangeTest` parameterizes `DeleteFilesInRange` tests over plain keys vs user-defined timestamp comparator behavior. It wraps `Put`, `Get`, and optional timestamped reads using `MinU64Ts()`.
- Local helpers include `DeletionTriggerOptions()`, `HaveOverlappingKeyRanges()`, `GetOverlappingFileNumbersForLevelCompaction()`, `VerifyCompactionResult()`, `PickFileRandomly()`, `FlushedFileCollector`, and `SstStatsCollector`.

## Covered APIs and Integration Points

The tests drive public and internal APIs:

- public DB APIs: `Put`, `Delete`, `SingleDelete`, `DeleteRange`, `Flush`, `CompactRange`, `CompactFiles`, `SetOptions`, `EnableAutoCompaction`, `PauseBackgroundWork`, `ContinueBackgroundWork`, `WaitForCompact`, `Close`, `DropColumnFamily`, `GetSnapshot`, `ReleaseSnapshot`, `GetLiveFilesMetaData`, `GetLiveFilesStorageInfo`, `GetColumnFamilyMetaData`, `GetProperty`, and `GetIntProperty`;
- utility/admin APIs: `DeleteFilesInRange`, `DeleteFilesInRanges`, `SstFileWriter`-related ingestion headers, and `ConcurrentTaskLimiter`;
- test-only hooks from `DBImpl`, `VersionSet`, `ColumnFamilyData`, and `DBTestBase`, such as `TEST_WaitForCompact`, `TEST_WaitForFlushMemTable`, `TEST_CompactRange`, `TEST_GetFilesMetaData`, `MoveFilesToLevel`, `FilesPerLevel`, and `NumTableFilesAtLevel`;
- sync-point instrumentation in compaction picker, `DBImpl::BackgroundCompaction`, `CompactionJob`, `TableCache`, `VersionSet`, `FlushJob`, `ThreadPoolImpl`, and filesystem direct-I/O open paths;
- option surfaces including `compaction_style`, `compaction_pri`, `max_subcompactions`, `level0_file_num_compaction_trigger`, `bottommost_level_compaction`, `change_level`, `target_level`, `target_path_id`, `exclusive_manual_compaction`, `allow_write_stall`, `ttl`, `periodic_compaction_seconds`, `daily_offpeak_time_utc`, `bottommost_file_compaction_delay`, `db_paths`, `cf_paths`, `compaction_thread_limiter`, `use_direct_io_for_flush_and_compaction`, and `use_direct_io_for_compaction_reads`.

## Main Control Flow and Behavioral Areas

### Deletion-triggered compaction and stats

`CompactionDeletionTrigger`, `CompactionDeletionTriggerReopen`, `DisableStatsUpdateReopen`, and `SkipStatsUpdateTest` build large key ranges, delete them, then verify that deletion-compensated file size accounting drives compaction and reduces physical size. They compare level compaction vs universal compaction and explicitly test reopen behavior with `skip_stats_update_on_db_open`. `CompactionWithDeletionsAndMinFileSize` adds the table-properties deletion collector and confirms files below the configured threshold are not selected.

`CompactionStatsTest` asserts running-compaction properties begin/end at zero and that internal per-reason stats match listener callbacks. `CompactionHasEmptyOutput` confirms compaction that drops all keys creates no output SST while flushes still emit table-creation callbacks.

### Manual and automatic compaction interactions

Many tests shape LSM state with flushes and `MoveFilesToLevel()`, then use manual compaction to verify selection:

- `ManualCompaction`, `ManualLevelCompactionOutputPathId`, `ManualCompactionPartial`, and disabled `ManualPartialFill` cover partial ranges, repeated level transitions, path selection, block-cache non-pollution, and concurrent manual/auto compaction.
- `ManualCompactionWithUnorderedWrite` verifies manual compaction waits correctly while unordered writes have written WAL but not memtable state, and that the newest value survives reopen.
- `ManualAutoRace`, `CancelCompactionWaitingOnRunningConflict`, and `CancelCompactionWaitingOnScheduledConflict` use sync points to force conflicts between auto compaction and exclusive/manual compaction, then assert retry or cancellation semantics.
- `CompactFilesPendingL0Bug`, `CompactFilesOverlapInL0Bug`, and `CompactFilesOutputRangeConflict` are regression tests for safe `CompactFiles()` picking when L0 files overlap by key/time range or when output ranges conflict with another scheduled compaction.

### Trivial moves, output levels, and file placement

`TrivialMoveOneFile`, `TrivialMoveNonOverlappingFiles`, `TrivialMoveTargetLevel`, `TrivialMoveToLastLevelWithFiles`, and `ForceBottommostLevelCompaction` assert when RocksDB can move SST metadata without rewriting data and when it must do non-trivial compaction. They validate exact `FilesPerLevel()` strings, unchanged file names/sizes for moved files, and counters from `DBImpl::BackgroundCompaction:TrivialMove`.

`LevelCompactionThirdPath`, `LevelCompactionPathUse`, and `LevelCompactionCFPathUse` test placement across multiple `db_paths` and per-column-family `cf_paths`. They verify SST counts per directory, data reads after reopen, and `GetLiveFilesStorageInfo()` directory/relative filename correctness.

`ConvertCompactionStyle` documents the migration path from leveled to universal compaction: reopening universal directly with non-L0 files fails, compacting to one L0 file first enables universal mode, and all keys remain visible after additional universal writes/compaction.

### Correctness around tombstones, snapshots, and key ordering

`UserKeyCrossFile1/2`, L0 issue-44 regressions, `OptimizedDeletionObsoleting`, `IntraL0CompactionDoesNotObsoleteDeletions`, `DeleteFileRangeFileEndpointsOverlapBug`, and the direct-I/O LevelIterator tombstone setup protect against old values reappearing when deletes cross file boundaries. Snapshot-related tests include `ZeroSeqIdCompaction`, `CompactBottomLevelFilesWithDeletions`, `DelayCompactBottomLevelFilesWithDeletions`, and `NoCompactBottomLevelFilesWithDeletions`, which verify bottommost file recompaction after snapshot release, optional delay, and no-compaction cases.

`DeleteFileRange` and `DeleteFilesInRanges` verify whole-file range deletion APIs across regular and timestamped comparators. They ensure partial range deletion only drops eligible files, complete deletion removes all files, and key visibility matches whether deleted files fully covered a range.

### Scheduling, pools, stalls, and limiters

`BGCompactionsAllowed` verifies automatic compaction scheduling debt across multiple column families and speed-up behavior. `CompactRangeBottomPri`, `FullCompactionInBottomPriThreadPool`, and `UniversalReduceFileLockingRepickNothing` validate bottom-priority pool forwarding, reduced file locking repick behavior, and correct no-op when intended universal inputs were already compacted by another job.

`CompactionLimiter` creates many column families with shared `ConcurrentTaskLimiter` instances and validates outstanding compaction tasks never exceed configured limits. It also checks a fully throttled limiter does not permanently block manual compaction.

`CompactRangeDelayedByL0FileCount`, `CompactRangeDelayedByImmMemTableCount`, `CompactRangeShutdownWhileDelayed`, `CompactRangeSkipFlushAfterDelay`, and `CompactRangeFlushOverlappingMemtable` define `CompactRangeOptions::allow_write_stall=false` behavior. Manual compaction delays flushes that would enter stall conditions, unblocks on CF drop/shutdown, skips redundant flushes after waiting, and only flushes memtables overlapping the requested key range.

`DBCompactionWaitForCompactTest` cases define `WaitForCompact()` semantics: it waits for reopen-triggered compaction debt, aborts when background work is paused if configured, returns shutdown status when DB closes while waiting, optionally flushes before waiting, optionally closes DB after waiting, handles WAL-disabled unpersisted data, and times out when a compaction job is held.

### TTL and periodic compaction

The TTL/periodic suite uses mock time:

- `RoundRobinTtlCompactionNormal` and `RoundRobinTtlCompactionUnsortedTime` verify round-robin compaction priority finds expired files across cursor positions and level layouts.
- `LevelCompactExpiredTtlFiles`, `LevelTtlCompactionOutputCuttingIteractingWithOther`, `LevelTtlCascadingCompactions`, and `LevelTtlBooster` verify TTL compactions delete expired dead data, maintain TTL output-cutting state, cascade overlapping ranges down levels, and boost priority before full expiry.
- `LevelPeriodicCompaction`, `LevelPeriodicCompactionOffpeak`, `LevelPeriodicCompactionWithOldDB`, `LevelPeriodicAndTtlCompaction`, and `LevelPeriodicCompactionWithCompactionFilters` test periodic file age metadata, off-peak adjustment, old manifests with zero creation times, interaction with TTL, and automatic periodic setting when compaction filters are installed.

These tests integrate with manifest/table property fields such as `file_creation_time`, `creation_time`, and `oldest_ancester_time`, often by forcing encoded fields to zero through sync points.

### Table readers, cache behavior, and direct I/O

`TestTableReaderForCompaction` checks table-cache lookup and table-reader creation counts around flush, compaction input iteration, and verification reads. `IntraL0Compaction` further verifies the output of L0-to-L0 compaction does not leave pinned index/filter blocks in the block cache.

`DirectIO` validates `use_direct_io_for_flush_and_compaction` controls output file direct writes. The direct compaction-read tests added in this chunk establish a newer contract:

- when `use_direct_io_for_compaction_reads` is off, compaction input `FileOptions` stay buffered and no `O_DIRECT` open is observed;
- when it is on, compaction opens fresh, bounded, ephemeral table readers for input files, avoids shared metadata cache, skips filters, and keeps user reads buffered;
- end-to-end tests on supported platforms prove actual kernel `O_DIRECT` opens occur for compaction inputs;
- the LevelIterator-with-tombstones setup builds L1+ range tombstone compactions to stress ephemeral reader lifetime and range tombstone iterator ownership.

## State and Persistence Behavior

The tests repeatedly close/reopen DBs to prove on-disk state is durable across WAL replay, manifest reload, compaction-style changes, path changes, and old metadata encodings. Persistent signals include:

- `FilesPerLevel()` and live-file metadata before/after manual and automatic compactions;
- physical SST presence via `CountFiles()`, `CountLiveFiles()`, `GetSstFileCount()`, and `Env::FileExists()`;
- key visibility after compaction, deletion, snapshot release, timestamped reads, and reopen;
- table properties used for TTL/periodic/deletion-triggered compaction;
- directory placement in `db_paths`, `cf_paths`, and `GetLiveFilesStorageInfo()`;
- manifest behavior under shutdown, incomplete compactions, file creation failure, and direct `Close()`.

Failure-injection and mock env behavior is important: partial compaction output-file creation failure must leave all L0 inputs intact and the DB reopenable; deletion of moved/obsolete files must be deferred until iterators release references; background shutdown must unblock waiting manual compactions with the right status.

## Dependencies

This chunk depends heavily on RocksDB internal test infrastructure:

- `db/db_test_util.h` and `DBTestBase` for DB lifecycle, column families, generated files, and assertions;
- compaction picker internals, `Compaction`, `VersionSet`, `VersionStorageInfo`, `ColumnFamilyData`, and `InternalStats`;
- `test_util/sync_point.h` for deterministic interleavings;
- mock/fault environments and mock clocks for I/O errors, direct I/O support, file counters, sleep/time control, and background thread control;
- table/cache components, block-based table options, SST partitioner factories, deletion collectors, user timestamp comparator wrappers, and concurrent task limiters.

The tests also rely on gtest parameterization and platform guards for Valgrind and direct-I/O support.

## Risks and Invariants Captured

- Compaction input picking must include all overlapping L0 files by key and sequence-time range; otherwise older values can reappear.
- Manual compaction conflict tracking must release scheduled/running counters on failure/cancel paths, or DB close can hang.
- Reduced universal file locking must safely repick or abandon bottom-priority intents when another compaction consumes intended inputs.
- Tombstones must be dropped only when lower-level key ranges prove they are obsolete; intra-L0 compaction must not drop tombstones merely because lower levels do not overlap.
- Snapshot-protected bottommost files need recompaction after snapshot release, but optional delay and threshold state must prevent premature rewrites.
- `allow_write_stall=false` cannot be implemented as unconditional flush; it must inspect stall state and memtable/range overlap.
- Direct I/O compaction reads cannot reuse buffered table readers from user reads; ephemeral readers must have correct metadata-cache and lifetime rules, especially with range tombstones and LevelIterator.
- Periodic/TTL compaction depends on stable file age metadata across old manifests and reopen; zeroed fields need conservative handling.
- Path selection and file deletion are persistence-sensitive; wrong directory or premature obsolete-file deletion breaks reopen and iterator safety.

## Test Signals

Primary pass/fail signals are `ASSERT_OK`/`ASSERT_NOK`, exact `FilesPerLevel()` expectations, file counts by level/path, listener callback counts, sync-point callback counters, ticker counts, key-value reads, `IsNotFound()` checks, status classes (`Aborted`, `TimedOut`, `ShutdownInProgress`, `ColumnFamilyDropped`, `Incomplete`), and direct-I/O open counters. Many tests also assert that no unexpected compaction reason occurs by inspecting `Compaction::compaction_reason()` at picker return.

For future changes in production compaction code, this chunk is a broad regression net. A failure here usually indicates either changed scheduling interleavings, changed compaction picking/metadata accounting, altered option sanitization, or a real correctness risk around file range conflict, tombstone preservation, or persistence across reopen.

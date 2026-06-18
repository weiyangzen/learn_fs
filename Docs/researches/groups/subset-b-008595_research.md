# subset-b-008595 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_compaction_flush.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_compaction_flush.cc

## Purpose

`db_impl_compaction_flush.cc` implements RocksDB `DBImpl`'s flush, compaction, manual compaction, background scheduling, and related observability paths. It is the operational center that converts in-memory memtables into persistent SST/blob metadata, selects and runs compactions, coordinates manual and automatic work, publishes new `SuperVersion`s, handles write-stall-aware waiting, and routes background errors into `ErrorHandler`.

The file sits above `FlushJob` and `CompactionJob`: it creates those jobs, enforces DB-wide scheduling and mutex contracts, handles WAL/MANIFEST ordering, and cleans obsolete files after jobs finish. It also implements public APIs such as `Flush()`, `CompactRange()`, `CompactFiles()`, `WaitForCompact()`, `EnableAutoCompaction()`, `PauseBackgroundWork()`, `AbortAllCompactions()`, and timestamp-history advancement.

## Important APIs, Types, and Functions

- `FlushMemTableToOutputFile()` is the single-CF flush path. It syncs closed WALs when needed, picks immutable memtables, prepares direct-write blob-file additions, runs `FlushJob`, installs a new `SuperVersion`, notifies listeners, updates `SstFileManagerImpl`, and records background errors.
- `AtomicFlushMemTablesToOutputFiles()` flushes multiple column families as one manifest-visible unit. It runs multiple `FlushJob`s, waits for all involved memtables to become installable in order, fsyncs distinct output directories, calls `InstallMemtableAtomicFlushResults()`, and rolls back memtable flush state on failure.
- `CompactRange()` and `CompactRangeInternal()` implement manual range compaction, including timestamp-aware range augmentation, optional `full_history_ts_low` persistence, pre-compaction flush, universal/FIFO/leveled strategy differences, bottommost compaction, and optional `change_level` refitting.
- `CompactFiles()` and `CompactFilesImpl()` implement explicit-file compaction. They sanitize input files, check conflicts and disk reservation, support manifest-only trivial moves, otherwise run a user-priority `CompactionJob`, and fill caller-visible output names and `CompactionJobInfo`.
- `RunManualCompaction()` owns `ManualCompactionState` queueing, exclusive/manual conflict handling, cancellation, scheduling into LOW or BOTTOM Env pools, and range continuation for partial manual compactions.
- `BackgroundFlush()`, `BackgroundCallFlush()`, `BackgroundCompaction()`, and `BackgroundCallCompaction()` are the Env worker entry points. They pop queues, execute work under the correct mutex/no-mutex phases, retry or sleep on transient failure, find/purge obsolete files, decrement scheduled/running counters, and signal waiters.
- `MaybeScheduleFlushOrCompaction()` is the scheduler. It consumes `unscheduled_flushes_` and `unscheduled_compactions_`, respects pause/error/shutdown/manual-exclusive gates, applies `GetBGJobLimits()`, and schedules `BGWorkFlush`, `BGWorkCompaction`, or bottom-priority compaction callbacks.
- `EnqueuePendingFlush()`, `EnqueuePendingCompaction()`, `PopFirstFromFlushQueue()`, `PickCompactionFromQueue()`, and queue helpers own `ColumnFamilyData` refs and queue flags.
- `NotifyOnFlushBegin()`, `NotifyOnFlushCompleted()`, `NotifyOnCompactionBegin()`, `NotifyOnCompactionPreCommit()`, `NotifyOnCompactionCompleted()`, and `BuildCompactionJobInfo()` populate listener-facing job metadata.
- `PauseBackgroundWork()`, `ContinueBackgroundWork()`, `DisableManualCompaction()`, `EnableManualCompaction()`, `AbortAllCompactions()`, and `ResumeAllCompactions()` coordinate operational gates around background activity.
- `InstallSuperVersionAndScheduleWork()` publishes a new column-family `SuperVersion`, recomputes global thresholds and memory accounting, enqueues follow-up compaction, and reschedules work.
- `WaitUntilFlushWouldNotStallWrites()`, `WaitForFlushMemTables()`, and `WaitForCompact()` implement user-visible waiting semantics around write-stall avoidance, flush completion, background drain, optional shutdown close, and background errors.
- `EnoughRoomForCompaction()` and `RequestCompactionToken()` integrate `SstFileManagerImpl` space accounting and `ConcurrentTaskLimiterImpl` task throttling.

## Control Flow

Manual flush starts in `Flush()` or `Flush(vector)`, then chooses `FlushMemTable()` or `AtomicFlushMemTables()` depending on DB options and `FlushOptions::force_atomic_flush`. The request path optionally waits until the hypothetical new immutable memtable/L0 file would not stall writes, joins write-thread queues, waits for pending writes, switches memtables, marks immutable lists as flush-requested, enqueues `FlushRequest`s, schedules background work, notifies listeners, and optionally waits through `WaitForFlushMemTables()`.

Background flush workers enter `BackgroundCallFlush()`, increment running counters, reserve pending output file number state, and call `BackgroundFlush()`. `BackgroundFlush()` pops one flush request, filters dropped or not-pending CFs, may reschedule a single-CF request to retain user-defined timestamps, builds `BGFlushArg`s and `SuperVersionContext`s, then calls `FlushMemTablesToOutputFiles()`. The actual flush path syncs closed WALs before permitting SST state to become newer than WAL state, picks memtables only after WAL ordering is safe, releases the DB mutex for file IO/listener callbacks, commits manifest edits inside `FlushJob`, and publishes `SuperVersion`s. `BackgroundCallFlush()` then finds obsolete files, purges outside the mutex, decrements counters, reschedules, fires pressure callbacks, and signals `atomic_flush_install_cv_` and `bg_cv_`.

Automatic compaction starts from `EnqueuePendingCompaction()` and `MaybeScheduleFlushOrCompaction()`. `BackgroundCallCompaction()` wraps counters, pending output capture, error sleep, obsolete-file cleanup, task-token release, pressure notification, and signaling. `BackgroundCompaction()` chooses between prepicked manual work, queued automatic work, intended bottom-priority repicks, deletion compaction, FIFO temperature trivial copy, trivial move, bottom-priority forwarding, and full `CompactionJob`. Full compaction runs `Prepare()` under mutex, releases the mutex for `Run()`, reacquires it for pre-commit listener notification and install, then publishes a `SuperVersion` and releases compaction files.

Manual compaction is queue-driven. `RunManualCompaction()` registers a stack-owned `ManualCompactionState`, optionally waits for all other compactions in exclusive mode, repeatedly asks the column family to pick a compaction for the remaining range, schedules it as prepicked work, waits on `bg_cv_`, and updates the range when only part was compacted. Pause/abort/cancel paths mark the state done with `Incomplete` status and may unschedule pending Env tasks.

`CompactRangeInternal()` layers policy above this scheduler. It can persist `full_history_ts_low`, flush overlapping memtables, find the first overlapped level using metadata or within-file iterator checks, run compactions level-by-level, force bottommost compaction when requested, and optionally call `ReFitLevel()` after pausing background work. `CompactFilesImpl()` bypasses picker policy by constructing explicit input compactions and can perform metadata-only trivial moves by writing a `VersionEdit` directly.

## State and Persistence Behavior

The durable state changes are WAL additions in MANIFEST, SST files, blob-file additions/garbage records, file-level moves/deletions in `VersionEdit`, `full_history_ts_low`, compact cursor updates, and new `SuperVersion` publication. Flush paths carefully order closed WAL sync and `ApplyWALToManifest()` before memtable picking when multi-CF or 2PC recovery requires WAL persistence to cover flushed SST contents.

Single-CF flush uses `FlushJob` with `write_manifest=true` and syncs the output directory. Atomic flush creates per-CF `FlushJob`s with deferred manifest writes, fsyncs distinct output directories, and commits the combined result with `InstallMemtableAtomicFlushResults()`. On atomic failure it cancels unexecuted jobs, rolls back executed memtables, evicts uninstalled table-cache entries, and preserves prepared direct-write blob generations for retry when the same immutable memtables still reference sealed blob files.

Compaction persistence flows through `CompactionJob::Install()`, `VersionSet::LogAndApply()`, or direct trivial-move edits. File-number capture through `CaptureCurrentFileNumberInPendingOutputs()` protects in-flight outputs from obsolete-file deletion. `ReleaseFileNumberFromPendingOutputs()` happens after job completion, followed by `FindObsoleteFiles()` and `PurgeObsoleteFiles()`.

`InstallSuperVersionAndScheduleWork()` is the visibility boundary for readers and later scheduling. It installs the new `SuperVersion`, updates `max_total_in_memory_state_`, resets bottommost/range-deletion marking thresholds, enqueues pending compaction for the affected CF, and calls the scheduler.

Queue state is reference counted. Non-atomic flushes set `queued_for_flush()` and hold a CF ref; atomic flushes intentionally bypass this dedup guard and rely on flush-in-progress filtering. Compaction queues set `queued_for_compaction()` and hold a CF ref until popped or deleted. Manual compactions are not heap-owned by the queue; the queue points at caller stack state while `RunManualCompaction()` waits.

Background error handling is central. Flush distinguishes WAL sync errors, MANIFEST write errors, SST write errors after WAL sync, shutdown, CF drop, and recovery flushes. Compaction maps IO status and `versions_->io_status()` into `BackgroundErrorReason::kCompaction` or `kManifestWrite`, and it requeues failed automatic compactions when background work is still allowed.

## Dependencies and Integration Points

This file integrates with RocksDB's major DB subsystems:

- LSM metadata: `ColumnFamilyData`, `Version`, `VersionStorageInfo`, `VersionSet`, `VersionEdit`, `SuperVersion`, `SuperVersionContext`, compaction pickers, and `InstallMemtableAtomicFlushResults()`.
- Flush and compaction execution: `FlushJob`, `Compaction`, `CompactionJob`, `CompactionJobStats`, `CompactionJobInfo`, `CompactionInputFiles`, `ManualCompactionState`, and `PrepickedCompaction`.
- WAL and recovery: `SyncWalImpl()`, `ApplyWALToManifest()`, `logs_with_prep_tracker_`, 2PC checks, recovery flush reasons, `ErrorHandler`, and recovery error state.
- BlobDB/direct-write: `BlobFilePartitionManager`, external blob file additions/garbages, protected sealed blob files, direct-write generation commit, and blob callback plumbing.
- IO and file management: `FileSystem`, `FSDirectory`, `WritableFileWriter`, `CopyFile`, `TableCache::ReleaseObsolete()`, `SstFileManagerImpl`, table/blob file naming, directory fsync options, and file checksum metadata.
- Scheduling: Env HIGH/LOW/BOTTOM thread pools, unschedule callbacks, `ConcurrentTaskLimiterImpl`, write-controller compaction speedup, background pressure snapshots, and condition variables.
- Observability and testing: `EventLogger`, `EventListener` callbacks, `ThreadStatusUtil`, histograms/tickers, log buffers, `IOSTATS`, perf context includes, and many `TEST_SYNC_POINT` hooks.

## Risks and Edge Cases

- Mutex boundaries are delicate. Flush/compaction jobs intentionally unlock around IO and callbacks; memtable picking, manifest install, queue mutation, and `SuperVersion` publication require `mutex_`.
- WAL/SST ordering is correctness-critical. If closed WAL sync or WAL manifest addition is skipped incorrectly, a flushed SST can survive crash without the WAL records needed by other CFs or prepared transactions.
- Atomic flush has many partial-failure states: executed jobs with uninstalled files, unexecuted picked memtables, dropped CFs, pending blob generations, directory fsync errors, and manifest failure all require different rollback or cleanup behavior.
- Manual compaction cancellation is cooperative and overloaded: pause and user cancellation both map to `ManualCompactionPaused`, while abort uses `CompactionAborted`. Exclusive manual compaction plus cancellation has a known limitation because waiting threads are not automatically awakened by a user-set canceled flag.
- Bottom-priority forwarding can hold an intended compaction and later repick under changed LSM state. The intended-compaction release/recompute path must keep compaction scores and file locks consistent.
- `ReFitLevel()` requires background work to be paused by caller; violating that precondition risks moving files across overlapping concurrent compaction outputs.
- Space checks are advisory and race with real disk use. `SstFileManagerImpl` reservation/completion accounting must be paired, and max-space-reached after flush is converted into a background error.
- Listener callbacks run without the DB mutex. Implementations can observe intermediate state and must not assume the same synchronization as internal code.
- `WaitForCompact(close_db=true)` sets `reject_new_background_jobs_` and calls `Close()` while temporarily unlocking; failure restores the flag, but callers must understand it is more than a passive wait.

## Test Signals

This file is heavily instrumented with `TEST_SYNC_POINT` and callback hooks around WAL sync, memtable picking, flush reschedule, atomic flush wait/install, manual compaction schedule/unschedule, compaction pick/run/install, trivial move, bottom-priority forwarding, refit level, abort/resume, and wait loops. Those hooks are direct signals that concurrency, error injection, and race-ordering tests cover this file.

Nearby tests are expected to exercise `db_compaction_test`, `compact_files_test`, flush/atomic-flush tests, FIFO temperature tests, manual pause/abort tests, listener callback tests, direct-write blob tests, and shutdown/wait-for-compact behavior. The debug helpers in `db_impl_debug.cc` also expose most internal counters and wait paths used by those tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_compaction_flush.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_debug.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_debug.cc

## Purpose

`db_impl_debug.cc` provides non-release `DBImpl::TEST_*` hooks compiled only when `NDEBUG` is not defined. It gives unit and stress tests controlled access to internal DB state and operations that are otherwise hidden behind production APIs: memtable/WAL switching, flush/compaction forcing, background wait loops, file metadata inspection, cache verification, periodic scheduler hooks, write-thread entry, and background error state.

The file is intentionally not part of production builds. Its role is to make internal invariants observable and to let tests create specific DB states without duplicating DB internals.

## Important APIs, Types, and Functions

- State readers: `TEST_GetLevel0TotalSize()`, `TEST_MaxNextLevelOverlappingBytes()`, `TEST_Current_Manifest_FileNo()`, `TEST_Current_Next_FileNo()`, `TEST_LogfileNumber()`, `TEST_GetBGError()`, `TEST_IsRecoveryInProgress()`, `TEST_BGCompactionsAllowed()`, `TEST_BGFlushesAllowed()`, `TEST_NumRunningBottomCompactions()`, `TEST_GetLastVisibleSequence()`, `TEST_GetSeqnoToTimeMapping()`, and `TEST_GetFilesToQuarantine()`.
- Metadata extraction: `TEST_GetFilesMetaData()` copies per-level `FileMetaData` and optionally blob metadata from the current version storage.
- Forced state transitions: `TEST_SwitchWAL()`, `TEST_SwitchMemtable()`, `TEST_FlushMemTable()`, `TEST_AtomicFlushMemTables()`, and `TEST_CompactRange()` invoke internal write/flush/compaction machinery with test reasons and controlled options.
- Wait helpers: `TEST_WaitForBackgroundWork()`, `TEST_WaitForFlushMemTable()`, `TEST_WaitForCompact()`, `TEST_WaitForPurge()`, and `TEST_WaitForPeriodicTaskRun()` expose blocking synchronization points.
- Lock/write helpers: `TEST_LockMutex()`, `TEST_UnlockMutex()`, `TEST_SignalAllBgCv()`, `TEST_BeginWrite()`, and `TEST_EndWrite()` allow tests to stage specific interleavings.
- Cache and file-lifetime helpers: `TEST_GetAllBlockCaches()`, `TEST_DeleteObsoleteFiles()`, and `TEST_VerifyNoObsoleteFilesCached()` validate cache/file cleanup invariants.
- Transaction/WAL-prep helpers: `TEST_FindMinLogContainingOutstandingPrep()`, `TEST_PreparedSectionCompletedSize()`, `TEST_LogsWithPrepSize()`, and `TEST_FindMinPrepLogReferencedByMemTable()` expose prepared-section tracking internals.
- Option/scheduler helpers: `TEST_GetLatestMutableCFOptions()`, `TEST_GetWalPreallocateBlockSize()`, and `TEST_GetPeriodicTaskScheduler()`.

## Control Flow

Most functions are thin wrappers that acquire `mutex_` or another internal mutex, read or call the underlying `DBImpl` method, and return the result. Column-family arguments are normalized by using the default CF when the caller passes null or by casting `ColumnFamilyHandleImpl` to access `ColumnFamilyData`.

`TEST_SwitchWAL()` and `TEST_SwitchMemtable()` enter the unbatched write-thread path before invoking internal switch routines so tests preserve the same write-thread invariants as production transitions. When `two_write_queues_` is enabled, `TEST_SwitchMemtable()` also enters/exits `nonmem_write_thread_`.

`TEST_FlushMemTable()` constructs `FlushOptions` or accepts supplied options and calls `FlushMemTable()` with `FlushReason::kTest`. `TEST_AtomicFlushMemTables()` similarly calls `AtomicFlushMemTables()` with test reason. `TEST_CompactRange()` calculates the expected output level for leveled versus universal/FIFO compaction and delegates to `RunManualCompaction()`.

`TEST_VerifyNoObsoleteFilesCached()` is the most substantial helper. In ASAN-like builds where heap allocation cleanup is required, it optionally locks the DB mutex, builds a set of live/quarantined SST and blob file numbers from all live versions, active/protected blob partition manager state, and `ErrorHandler` quarantine state, then applies a callback to all table-cache entries asserting every cached file is still live or quarantined.

## State and Persistence Behavior

This file does not introduce independent persistent state. Instead, it invokes production paths that may persist state: WAL switching can create/sync WAL metadata through normal internals, memtable switching changes mutable/immutable lists, flush and compaction wrappers create SSTs and MANIFEST edits, and obsolete-file deletion can remove files.

Read helpers expose in-memory and persisted metadata snapshots while holding the appropriate mutex. `TEST_GetFilesMetaData()` copies current version file metadata by value, and blob metadata by shared pointer, so tests can inspect LSM layout without owning internal `VersionStorageInfo`.

The cache verification helper treats live versions, direct-write blob manager active/protected files, and quarantined files as allowed cache residents. Any table-cache entry outside that set is considered an obsolete open-file leak and triggers assertion diagnostics.

## Dependencies and Integration Points

`db_impl_debug.cc` depends on core DB internals (`ColumnFamilyData`, `VersionStorageInfo`, `ErrorHandler`, write threads, WAL/prepared trackers), blob subsystems (`BlobFileCache`, `BlobFilePartitionManager`), block-based table options for cache discovery, `PeriodicTaskScheduler`, and thread-status/cast utilities.

Its main integration point is the RocksDB test suite. It provides direct hooks for tests that need deterministic control over compaction/flush scheduling, background waits, file cleanup, WAL numbering, block cache membership, mutable CF options, and scheduler execution.

## Risks and Edge Cases

- These functions are compiled only in debug builds. Tests depending on them cannot run against release binaries without alternate hooks.
- Several helpers expose raw internal synchronization primitives. Misusing `TEST_LockMutex()`/`TEST_UnlockMutex()` or write-thread entry helpers can deadlock tests or violate production lock ordering.
- Forced flush/compaction helpers execute real production side effects, so tests must clean up DB files and background work just as with public APIs.
- `TEST_VerifyNoObsoleteFilesCached()` is intentionally restricted to heap-cleanup/ASAN-style builds because it scans caches and can be expensive or noisy in broad test configurations.
- Some readers return values without taking the DB mutex, such as current next file number through `VersionSet`; tests should treat these as diagnostic helpers rather than general concurrency-safe APIs unless the underlying method provides safety.

## Test Signals

Every symbol in this file is itself a test signal. The breadth of exposed helpers indicates that RocksDB tests assert internal L0 sizing, manifest/file-number allocation, exact file metadata, manual compaction behavior, atomic flush behavior, background error recovery, purge completion, block-cache ownership, prepared transaction WAL retention, periodic task execution, stats-history memory accounting, and obsolete-file cache cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_debug.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_experimental.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_experimental.cc

## Purpose

`db_impl_experimental.cc` implements two experimental `DBImpl` maintenance APIs: `SuggestCompactRange()` and `PromoteL0()`. Both manipulate compaction metadata directly under the DB mutex to influence LSM layout without performing a normal write-path operation.

`SuggestCompactRange()` marks existing files in a key range as compaction candidates and schedules background compaction. `PromoteL0()` performs a metadata-only promotion of non-overlapping L0 files into an empty target level by writing a MANIFEST edit.

## Important APIs, Types, and Functions

- `SuggestCompactRange(ColumnFamilyHandle*, const Slice* begin, const Slice* end)` converts optional user-key bounds to internal min/max keys, scans non-last non-empty levels for overlapping files, sets `FileMetaData::marked_for_compaction`, recomputes compaction score, enqueues the CF, and schedules background work.
- `PromoteL0(ColumnFamilyHandle*, int target_level)` validates the target level, sorts L0 files by largest key, rejects files currently compacting or overlapping L0 ranges, verifies levels `1..target_level` are empty, writes a `VersionEdit` that deletes files from L0 and adds them to the target level, applies the edit through `VersionSet::LogAndApply()`, and publishes a `SuperVersion`.
- Supporting types include `ColumnFamilyHandleImpl`, `ColumnFamilyData`, `VersionStorageInfo`, `InternalKey`, `InternalKeyComparator`, `FileMetaData`, `VersionEdit`, `JobContext`, `ReadOptions`, and `WriteOptions`.

## Control Flow

`SuggestCompactRange()` is advisory. It casts the handle, builds internal bound keys only for provided endpoints, locks `mutex_`, then iterates from level 0 through the level before the highest non-empty level. For each level it calls `GetOverlappingInputs()` and flips `marked_for_compaction` on each overlapping file. After marking, it recomputes compaction scores with latest mutable CF options and `full_history_ts_low`, enqueues pending compaction for the column family, and invokes `MaybeScheduleFlushOrCompaction()`.

`PromoteL0()` is stricter because it directly changes persistent LSM metadata. It rejects `target_level < 1`, then under `mutex_` rejects target levels outside the configured number of levels. It copies and sorts L0 file metadata by largest internal key, checks no file is already being compacted, and verifies adjacent sorted files do not overlap. It then requires every level from 1 through the target to be empty. Only after these invariants pass does it build a `VersionEdit` deleting each file from L0 and adding the same file metadata to the target level. `LogAndApply()` persists the edit to MANIFEST; on success `InstallSuperVersionAndScheduleWork()` makes the new layout visible and schedules any resulting work.

## State and Persistence Behavior

`SuggestCompactRange()` changes in-memory file metadata by setting `marked_for_compaction`. It does not write a manifest edit itself, but recomputed compaction score and queueing can lead to future compactions that persist new SST/MANIFEST state.

`PromoteL0()` is a manifest-persisted metadata move. It does not rewrite SST bytes and does not create new table files. The same file numbers, sizes, key bounds, sequence bounds, temperature, blob linkage, checksums, unique IDs, range-deletion sizes, tail sizes, timestamp persistence flags, and min/max timestamps are re-added at the target level. Its successful completion installs a new `SuperVersion`, flushes the info log, and cleans the `JobContext`.

Neither function flushes memtables first. They operate on the current version's files and assume their invariants are sufficient for safe metadata manipulation.

## Dependencies and Integration Points

These APIs depend on `db_impl.h`, `column_family.h`, `version_set.h`, `job_context.h`, logging, status, and checked casts. They integrate with the same scheduler and versioning paths used by the larger compaction implementation: `VersionStorageInfo::ComputeCompactionScore()`, `EnqueuePendingCompaction()`, `MaybeScheduleFlushOrCompaction()`, `VersionSet::LogAndApply()`, and `InstallSuperVersionAndScheduleWork()`.

`PromoteL0()` is closely related to trivial move/refit logic in `db_impl_compaction_flush.cc`, but is narrower: it only promotes L0 to a higher empty level when L0 files are mutually non-overlapping and none are being compacted.

## Risks and Edge Cases

- `SuggestCompactRange()` only marks files in existing levels before the final non-empty level. If a range only overlaps the bottommost non-empty level, the function may mark nothing and still return OK.
- Marking files for compaction is advisory and can be delayed or ignored by later picker decisions if options, errors, pauses, or scheduling state prevent compaction.
- `PromoteL0()` assumes sorted L0 files are non-overlapping. This excludes common L0 states with overlapping flush outputs, so callers must only use it after constructing a compatible L0.
- `PromoteL0()` requires all levels up to the target to be empty. It will not merge with existing target-level files or compact through intermediate levels.
- The promotion is metadata-only. Incorrect overlap validation would create invalid leveled-LSM invariants without rewriting data, so the comparator checks and empty-level checks are correctness-critical.
- The code calls `job_context.Clean()` on early validation failures while still under the mutex even though the job context has not accumulated normal job work; this is harmless but shows the function is using shared cleanup idioms rather than a bespoke context.

## Test Signals

Tests should cover advisory marking and scheduling in `SuggestCompactRange()`, including null bounds, partial bounds, and no-overlap ranges. `PromoteL0()` needs tests for invalid target levels, target level out of range, files being compacted, overlapping L0 files, non-empty intermediate/target levels, successful manifest edits, and preservation of all file metadata fields during the L0-to-target move.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_experimental.cc -->

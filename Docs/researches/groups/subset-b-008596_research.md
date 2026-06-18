# subset-b-008596 Research

Work item: `subset-b-008596`

This grouped report covers the RocksDB `db_impl` file/open/read-only/follower slice. Each section is delimited for reconciliation into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_files.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_files.cc

## Purpose

`db_impl_files.cc` owns DBImpl file lifecycle decisions: determining which WAL, SST, blob, manifest, OPTIONS, info-log, temp, and identity files are live; suppressing or re-enabling deletion; purging obsolete files; computing minimum WAL retention for recovery; maintaining DB identity; and updating the next file number after recovery. It is a central persistence-safety component because it decides when durable artifacts can be deleted, recycled, archived, or retained.

## Important APIs, Types, And Functions

- `DBImpl::DisableFileDeletions`, `DisableFileDeletionsWithLock`, `EnableFileDeletions`, and `IsFileDeletionsEnabled` implement the public deletion gate via `disable_delete_obsolete_files_`.
- `DBImpl::FindObsoleteFiles(JobContext*, bool force, bool no_full_scan)` fills a `JobContext` with live file numbers, delete candidates, WAL state, manifest state, pending outputs, protected blob files, quarantined files, and optional full directory scan candidates.
- `DBImpl::PurgeObsoleteFiles(JobContext&, bool schedule_only)` converts the `JobContext` into concrete delete/archive/recycle/cache-release actions without holding the DB mutex for the slow path.
- `DBImpl::DeleteObsoleteFileImpl` performs actual file deletion and emits table/blob deletion events.
- `DBImpl::DeleteObsoleteFiles` is the mutex-held full-scan entry point used after open and in other cleanup paths.
- `DBImpl::ShouldKeepBlobFileDuringPurge` and the file-local `ShouldKeepFooterlessBlobFile` protect blob files that are tracked, active for direct write, or not yet footer-complete.
- `GetDBRecoveryEditForObsoletingMemTables`, `PrecomputeMinLogNumberToKeepNon2PC`, `PrecomputeMinLogNumberToKeep2PC`, and `FindMinPrepLogReferencedByMemTable` compute WAL retention edits after flush or mempurge, including two-phase-commit prepared-section retention.
- `DBImpl::SetupDBId` and `SetDBId` reconcile DB identity between MANIFEST and `IDENTITY`.
- `DBImpl::CollectAllDBPaths` and `MaybeUpdateNextFileNumber` discover DB/CF paths and ensure recovered file-number allocation cannot collide with on-disk files.

## Control Flow

Deletion control starts with `FindObsoleteFiles`. Under `mutex_`, it exits early if deletion is disabled, decides whether to perform a full filesystem scan based on `force`, `no_full_scan`, and `delete_obsolete_files_period_micros`, snapshots retention state into the `JobContext`, gathers obsolete files from `VersionSet`, marks files grabbed for purge, records manifest/log thresholds, and either collects all candidate files from DB/WAL/log directories or removes still-live files from the version-provided delete lists. It then increments `pending_purge_obsolete_files_` before crossing into WAL cleanup so readers of sorted WALs can wait for purge completion.

WAL cleanup in `FindObsoleteFiles` coordinates `mutex_`, `wal_write_mutex_`, `wal_sync_cv_`, `alive_wal_files_`, `logs_`, `wal_recycle_files_`, and `wals_to_free_`. WALs older than `MinLogNumberToKeep()` are either moved to the recycle list or scheduled for deletion, their sizes are removed from `wals_total_size_`, and old log writers are detached after waiting for in-flight syncs. The DB mutex can be temporarily released while closing inactive WAL files, then reacquired before returning.

`PurgeObsoleteFiles` runs the slower side. It builds live/recycle/quarantine sets, expands explicit SST/blob/WAL/manifest delete lists into candidate file names, releases table-cache handles for obsolete SSTs, deduplicates candidates, keeps the newest two OPTIONS files adjusted by `min_options_file_number`, closes detached WAL writers, and then evaluates each candidate by `FileType`. WALs are kept if above the min log, equal to prev log, or marked for recycling; manifests are kept if current or newer; table files are kept if live or pending; blob files are kept if live, pending, protected, newer than next file, or footerless/tracked; temp/options/current/lock/identity/meta files have their own keep rules. Files not owned by this DB instance are skipped. WALs can be archived rather than deleted when TTL or size limit is configured. Deletions can be immediate or scheduled through pending purge.

The WAL-retention helpers compute manifest edits for recovery cleanup. Non-2PC mode combines the flushed CF's new log number with other CFs' unflushed-data minimum. 2PC mode additionally considers outstanding prepared transactions in `LogsWithPrepTracker` and prepared sections still referenced by live or immutable memtables.

DB identity setup first tries to read `IDENTITY` for existing DBs and compare it with any MANIFEST DB ID. If missing or invalid, it generates a unique ID when needed and writes `IDENTITY` unless read-only or `write_identity_file` disables it. `MaybeUpdateNextFileNumber` scans every DB and CF path, records existing table/blob files into the recovery context, advances `next_file_number_` above any on-disk number, and emits a recovery edit unless the recovery-manifest optimization can skip a noop.

## State And Persistence Behavior

Persistent artifacts are protected by several independent retention gates: `pending_outputs_` for files being produced, `min_options_file_numbers_` for remotely referenced OPTIONS files, `VersionSet` live file sets, active/protected blob direct-write file numbers, WAL log numbers, manifest numbers, WAL tracking state, WAL recycling state, and quarantine from the error handler. `pending_purge_obsolete_files_` is the coordination bridge between discovery and actual purge. File deletion affects table cache, blob/table deletion listeners, WAL manager archive state, delete scheduler state, info-log retention, and optional WAL recycling.

`SetupDBId` persists or validates DB identity, while `MaybeUpdateNextFileNumber` persists file-number allocator advancement through `RecoveryContext::UpdateVersionEdits`. The file also records existing data files so higher-level open code can track them with the SST file manager.

## Dependencies And Integration Points

This file integrates with `VersionSet`, `ColumnFamilyData`, `MemTableList`, `LogsWithPrepTracker`, `JobContext`, `TableCache`, `BlobFilePartitionManager`, `WalManager`, `DeleteScheduler`, `SstFileManagerImpl`, `EventHelpers`, `FileSystem`/`Env`, and filename parsing helpers. It is called by open/recovery, flush/compaction cleanup, manual file-deletion APIs, WAL recovery, follower catch-up cleanup, and error-handling quarantine flows.

## Risks And Edge Cases

- Incorrect candidate classification can delete live SST/blob/WAL files or leak obsolete files indefinitely.
- Full scans race with in-progress direct-write blob files; the footerless-blob check is intentionally conservative.
- WAL cleanup has lock-order and sync-wait complexity. Regressions can deadlock writers or free a log writer while it is syncing.
- Secondary/follower ownership must be respected through `OwnTablesAndLogs`; otherwise one DB instance can delete another instance's files.
- `MaybeUpdateNextFileNumber` must handle crash-created files at exactly the previous next number to avoid allocator collision.
- 2PC WAL retention must account for outstanding prepared transactions and memtables with prepared sections; missing one can break recovery.
- Delete scheduling versus immediate deletion affects durability ordering, directory fsync, rate limiting, and test determinism.

## Test Signals

Useful test coverage includes deletion-disable nesting, full-scan and no-full-scan obsolete cleanup, WAL recycle and archive behavior, pending-output protection, blob direct-write/footerless retention, DB identity mismatch/missing-file recovery, best-efforts recovery file-number advancement, 2PC prepared WAL retention, secondary/follower file ownership, and crash/restart tests with created but unmanifested SST/blob/WAL files. The file has many `TEST_SYNC_POINT` hooks around deletion, WAL closing, blob retention, and recovery edit emission that are intended for race and fault-injection tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_files.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_follower.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_follower.cc

## Purpose

`db_impl_follower.cc` implements follower-mode DB open and refresh. A follower opens a local DB path backed by an on-demand filesystem pointing at a leader/source path, replays the leader MANIFEST through `ReactiveVersionSet`, creates local links to needed leader files, and periodically tails the MANIFEST to keep read state current. It is a read-scaling mode that differs from ordinary read-only open because it keeps catching up while the leader continues to evolve.

## Important APIs, Types, And Functions

- `DBImplFollower::DBImplFollower` constructs a `DBImplSecondary` with an empty secondary path, stores the wrapped `Env`, source path, condition variable, and stop flag.
- `DBImplFollower::~DBImplFollower` delegates to `Close`.
- `DBImplFollower::Recover` replays the MANIFEST with `ReactiveVersionSet::Recover`, creates the default column-family handle, records internal stats, and starts a dedicated periodic catch-up thread.
- `DBImplFollower::TryCatchUpWithLeader` tails and applies new MANIFEST records with `ReactiveVersionSet::ReadAndApply`.
- `DBImplFollower::PeriodicRefresh` sleeps for `follower_refresh_catchup_period_ms`, retries catch-up according to `follower_catchup_retry_count` and `follower_catchup_retry_wait_ms`, and stops when requested.
- `DBImplFollower::Close` stops and joins the catch-up thread, releases captured pending output file numbers, and closes the base DBImpl.
- `DB::OpenAsFollower` overloads build options, validate/create the local follower path, wrap the filesystem with `NewOnDemandFileSystem`, create a logger if needed, install `ReactiveVersionSet`, recover, create handles, install superversions, and publish the DB pointer.

## Control Flow

`DB::OpenAsFollower(Options, ...)` normalizes the single-default-CF case into the multi-CF overload. The multi-CF overload checks or creates `dbname`, constructs a `CompositeEnvWrapper` whose filesystem can fetch files on demand from `src_path` into `dbname`, creates an info log if needed, constructs `DBImplFollower`, replaces its `versions_` with `ReactiveVersionSet`, initializes `ColumnFamilyMemTablesImpl`, records whether WAL dir equals DB path, then calls `Recover` under `mutex_`.

`Recover` requires the DB mutex. It calls `ReactiveVersionSet::Recover` with the manifest reader and reporter, handles a failed manifest-reader status by permitting the unchecked error, creates the default column-family handle on success, and starts `catch_up_thread_`.

`TryCatchUpWithLeader` runs later from the refresh thread. It locks `mutex_`, asks `ReactiveVersionSet::ReadAndApply` to apply new manifest entries, releases and recaptures a pending-output file number around `current_next_file_number`, logs last sequence and next file number, and for each changed CF logs summary information. For non-dropped changed CFs, if the current memtable earliest sequence is older than the new last sequence, it moves the old memtable to immutable state, constructs fragmented range tombstones, and installs a fresh memtable with earliest sequence equal to `LastSequence`. It removes obsolete immutable memtables and installs a new superversion for each changed CF. It also deletes files returned by `ReadAndApply`, then outside that lock uses normal `FindObsoleteFiles`/`PurgeObsoleteFiles` cleanup.

`PeriodicRefresh` uses its private `mu_`/`cv_` for sleeping and shutdown notification, not the DB mutex. On each period it attempts catch-up repeatedly until success, retry exhaustion, or stop. `Close` sets `stop_requested_`, signals the condition variable, joins the thread, releases the pending output iterator, and calls `DBImpl::Close`.

## State And Persistence Behavior

Follower mode persists local metadata and linked/fetched files in `dbname`, while source data is accessed through an on-demand filesystem rooted at `src_path`. The code captures a pending output number during catch-up to keep cleanup from deleting files at or above the reactive next-file boundary. It maintains normal column-family superversion state for readers, but it does not create user-write WALs. `OwnTablesAndLogs()` currently returns true with a TODO about read-scaling deletion semantics, meaning purge behavior is intentionally conservative but still owner-like in this implementation.

## Dependencies And Integration Points

The follower depends on `DBImplSecondary`, `ReactiveVersionSet`, `CompositeEnvWrapper`, `NewOnDemandFileSystem`, manifest reader/reporting state from the base implementation, `ColumnFamilyMemTablesImpl`, `ColumnFamilyHandleImpl`, memtable/superversion machinery, file deletion helpers from `db_impl_files.cc`, and DB open entry points. It integrates with thread-status/logging, perf sync points, and the regular column-family handle API after open.

## Risks And Edge Cases

- Catch-up mutates versions, memtables, and superversions while readers may be active; correct locking and superversion install/cleanup are critical.
- The private refresh condition variable and DB mutex are separate; shutdown must wake sleeping retry loops promptly.
- Manifest tailing can fail transiently; the current TODO notes missing robust retry/error notification beyond local retries.
- File deletion for read scaling is called out as incomplete. Incorrect ownership or pending-output tracking could remove files still needed by the follower.
- Dropped column families are skipped for logging but changed-CF iteration must avoid installing reader state for dropped CFs.
- Local/source DB identity misconfiguration is not fully prevented; comments call out a future local `IDENTITY` cross-check.

## Test Signals

High-value tests should open as follower, verify default and named CF handles, force manifest catch-up, exercise dropped CFs, validate superversion replacement while iterators/readers exist, inject `ReadAndApply` failures and retry waits, test clean shutdown while sleeping and while catching up, verify on-demand links survive leader compaction/deletion, and assert obsolete cleanup does not delete needed source-linked files. Existing sync points around `TryCatchUpWithLeader` support deterministic catch-up race tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_follower.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_follower.h -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_follower.h

## Purpose

`db_impl_follower.h` declares `DBImplFollower`, the follower-mode DB implementation used by `DB::OpenAsFollower`. It specializes `DBImplSecondary` for a reactive, manifest-tailing read-scaling instance that uses a local DB path plus a source/leader path.

## Important APIs, Types, And Functions

- `class DBImplFollower : public DBImplSecondary` inherits secondary/read-only behavior and overrides recovery and close.
- The constructor takes sanitized `DBOptions`, an owned `Env`, `dbname`, and `src_path`.
- `~DBImplFollower()` closes the instance.
- `Status Close() override` stops background catch-up before base close.
- `OwnTablesAndLogs() const override` currently returns true, with a TODO explaining file deletion semantics for read scaling still need refinement.
- `Recover(...) override` has the same signature shape as `DBImpl::Recover` but ignores write/retry parameters that do not apply to follower recovery.
- Private helpers `TryCatchUpWithLeader` and `PeriodicRefresh` implement background manifest tailing.
- Private state includes `env_guard_`, `catch_up_thread_`, `stop_requested_`, `src_path_`, a private mutex/condition variable pair, and `pending_outputs_inserted_elem_`.

## Control Flow

The header makes `DB` a friend so open factories can construct and initialize `DBImplFollower` directly. Normal construction stores the environment wrapper and source path. Recovery is protected and called by open. Once recovered, the implementation starts `PeriodicRefresh`, which calls `TryCatchUpWithLeader` until `Close` sets `stop_requested_` and joins the thread.

## State And Persistence Behavior

`env_guard_` owns the composite/on-demand environment for the follower lifetime. `src_path_` identifies the leader/source DB path. `pending_outputs_inserted_elem_` pins a file-number boundary during reactive apply so obsolete-file cleanup treats freshly observed or soon-to-be-linked files as protected. The private `mu_`/`cv_` are lifecycle controls for the refresh thread and are separate from DBImpl's main mutex.

## Dependencies And Integration Points

The declaration depends on `db_impl.h`, `db_impl_secondary.h`, `logging`, and `port` threading primitives. Its protected overrides plug into the DBImpl open/recovery lifecycle, while private helpers integrate with `ReactiveVersionSet` in the `.cc` file.

## Risks And Edge Cases

- Returning true from `OwnTablesAndLogs` is explicitly marked provisional and affects purge ownership.
- The class owns a background thread; destructors and `Close` must be idempotent enough to handle open failures and explicit close.
- The recovery signature ignores several base parameters, so future DBImpl recovery contract changes must be reflected here.
- `pending_outputs_inserted_elem_` is a unique pointer to a list iterator; release/reset ordering matters for cleanup safety.

## Test Signals

Compile-time coverage should ensure all DBImpl recovery/close overrides still match the base class. Runtime tests should cover construction through `DB::OpenAsFollower`, repeated `Close`, destructor close after partial initialization, thread wakeup, and purge behavior while `pending_outputs_inserted_elem_` is set.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_follower.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_open.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_open.cc

## Purpose

`db_impl_open.cc` implements normal RocksDB DB opening and recovery. It sanitizes and validates options, creates brand-new DB metadata, locks and recovers existing DBs, replays MANIFEST and WAL files, flushes recovered memtables when needed, creates the next writable WAL, persists recovery edits/options/identity, initializes hidden persistent-stats state, schedules cleanup/background work, supports async WAL precreation and async table-file opening, and exposes `DB::Open`/`DB::OpenAndTrimHistory` entry points.

## Important APIs, Types, And Functions

- `SanitizeOptions` normalizes DB/CF options, creates default objects, adjusts thread pools, WAL recycling/compression, WAL/db paths, rate limits, and SST file manager defaults.
- `DBImpl::ValidateOptions` and the file-local `ValidateOptionsByTable` reject incompatible DB/CF options.
- `DBImpl::NewDB` creates MANIFEST-000001, writes the initial `VersionEdit`, syncs it, and writes `CURRENT`.
- `DBImpl::CreateAndNewDirectory` and `Directories::SetDirectories` create/open DB, WAL, and data directories.
- `DBImpl::Recover` is the main manifest/WAL recovery routine used by read-write and read-only open paths.
- Persistent stats helpers: `InitPersistStatsColumnFamily` and `PersistentStatsProcessFormatVersion`.
- Recovery edit/filter helpers: `LogAndApplyForRecovery`, `InvokeWalFilterIfNeededOnColumnFamilyToWalNumberMap`, and `InvokeWalFilterIfNeededOnWalRecord`.
- WAL replay pipeline: `RecoverLogFiles`, `SetupLogFilesRecovery`, `ProcessLogFiles`, `ProcessLogFile`, `InitializeLogReader`, `ProcessLogRecord`, `InitializeWriteBatchForLogRecord`, `InsertLogRecordToMemtable`, `MaybeWriteLevel0TableForRecovery`, `HandleNonOkStatusOrOldLogRecord`, `UpdatePredecessorWALInfo`, `FinishLogFileProcessing`, `MaybeHandleStopReplayForCorruptionForInconsistency`, `MaybeFlushFinalMemtableOrRestoreActiveLogFiles`, `GetLogSizeAndMaybeTruncate`, `RestoreAliveLogFiles`, and `WriteLevel0TableForRecovery`.
- Open entry points: `DB::Open`, `DB::OpenAndTrimHistory`, and `DBImpl::Open`.
- WAL creation and async helpers: `CreateWALWriter`, `StartWALFile`, `CreateWAL`, `AsyncWALPrecreateEnabled`, `MaybeScheduleAsyncWALPrecreate`, `WaitForAsyncWALPrecreate`, and `BGWorkAsyncWALPrecreate`.
- Async file-open helpers: `ScheduleAsyncFileOpening`, `MarkAsyncFileOpenNotNeeded`, and `BGWorkAsyncFileOpen`.

## Control Flow

`DB::Open` converts `Options` into DB/CF descriptors, optionally adds the hidden persistent-stats CF, sets thread tracking, and calls `DBImpl::Open`, retrying once when manifest read corruption can be reconstructed by the filesystem. `DBImpl::Open` validates options, creates directories and archival directory, constructs `DBImpl`, locks `options_mutex_` and `mutex_`, and calls `Recover`.

`Recover` handles the persistent metadata phase. In read-write mode it creates directories, locks `LOCK`, checks `CURRENT` or, in best-efforts mode, searches for a non-empty MANIFEST, creates a new DB if allowed, checks `error_if_exists`, and verifies filesystem/direct-I/O compatibility. It then recovers the `VersionSet` from MANIFEST or best-efforts `TryRecover`, possibly records trivial LSM moves for dynamic-level migration, reconciles/persists DB ID, updates next file number, creates CF directories, and scans WAL files. WAL verification can require tracked WALs in MANIFEST to match the directory; disabling manifest WAL tracking emits a safety edit deleting old tracked WAL state. It enforces read-only flags that reject non-empty WALs when requested, then sorts and replays WALs through `RecoverLogFiles`.

The WAL replay pipeline starts with `SetupLogFilesRecovery`, which creates per-CF `VersionEdit`s, logs a recovery-started event, invokes the WAL filter with the CF-to-log map, and computes the minimum WAL to keep. `ProcessLogFiles` iterates sorted WAL numbers and calls `ProcessLogFile`. Each WAL is marked used, opened through `InitializeLogReader`, then records are read in a loop. `ProcessLogRecord` decodes the write batch, reconciles timestamp-size differences, updates protection info/checksums, validates sequence numbers, allows a `WalFilter` to ignore/modify/stop/corrupt the record, inserts valid writes into memtables, and may flush scheduled memtables to L0 during recovery. After each WAL, predecessor metadata is updated, corruption/old-record handling applies the configured `WALRecoveryMode`, sequence numbers are published, and final recovery either flushes remaining memtables, records log-number edits, emits WAL deletion/min-log edits, restores active log files for `avoid_flush_during_recovery`, or truncates preallocated WAL tail space.

`WriteLevel0TableForRecovery` flushes a recovered memtable under the DB open path. It reserves a pending output number, builds a level-0 table and possible blob files with `BuildTable`, verifies memtable/output counts when configured, fsyncs the data directory before publishing the edit, adds file/blob additions to the `VersionEdit`, handles user-defined timestamp history cutoff movement, updates compaction/flush stats, and releases the pending output.

After `Recover`, `DBImpl::Open` creates a new writable WAL, optionally writes and syncs an empty batch at a recovered PIT sequence boundary, logs and applies all recovery edits, removes obsolete identity if identity-file writing is disabled, initializes persistent stats, prepopulates sequence-time mapping for new DBs, creates requested column-family handles or missing CFs, initializes blob direct write, installs superversions, validates memtable capabilities, writes an OPTIONS file, marks the DB opened, tracks existing files with `SstFileManager`, cleans trash and obsolete files, schedules flush/compaction, async file opening, async WAL precreation, syncs any buffered WAL header/dummy data, starts periodic tasks, registers seqno-time workers, and finally publishes the `unique_ptr<DB>`.

`DB::OpenAndTrimHistory` wraps `DB::Open`, rejects `avoid_flush_during_recovery`, force-compacts timestamp-enabled CFs at the trim timestamp, and cleans up handles/DB on failure.

## State And Persistence Behavior

This file creates and mutates the core durable state: `CURRENT`, MANIFEST/version edits, WAL files, `IDENTITY`, OPTIONS files, recovered L0 SST/blob files, tracked WAL metadata, min-log retention, per-CF log numbers, DB/session IDs, persistent stats CF keys, and sequence/time metadata. It carefully alternates mutex-held metadata updates with unlocked IO-heavy work. Recovery edits are accumulated in `RecoveryContext` and atomically persisted through `VersionSet::LogAndApply`.

Runtime state initialized here includes `db_lock_`, `default_cf_handle_`, `persist_stats_cf_handle_`, `logs_`, `alive_wal_files_`, `cur_wal_number_`, `min_wal_number_to_recycle_`, write-buffer recovery thresholds, flush/trim schedulers, superversions, thread-status CF info, error-handler auto-recovery, SST file manager tracking/reserved disk buffer, async WAL precreate state, and async file-open state.

## Dependencies And Integration Points

The file integrates with almost every DBImpl subsystem: `VersionSet`, `ColumnFamilyData`, `Manifest`, `WriteBatchInternal`, memtables, `BuildTable`, blob file additions, WAL reader/writer and compression/tracking, `WalFilter`, `SstFileManagerImpl`, `DeleteScheduler`, persistent stats history, sequence-time workers, table cache preopening, thread status, rate limiter, Env/FileSystem, options sanitation, and event logging. It also interacts with read-only open through `Recover(read_only=true)` and with `db_impl_files.cc` through DB identity, next-file-number updates, obsolete cleanup, and WAL retention.

## Risks And Edge Cases

- Recovery ordering is delicate: files must be durable before MANIFEST edits reference them, new WAL headers/dummy PIT records must be synced, and recovery edits must be applied before public DB exposure.
- WAL recovery mode differences are subtle. `kPointInTimeRecovery`, `kSkipAnyCorruptedRecords`, `kTolerateCorruptedTailRecords`, and `kAbsoluteConsistency` produce different replay stop/fail behavior.
- WAL filters can change batches but must not increase record count; bad filter behavior can corrupt recovery semantics.
- Timestamp-size reconciliation and user-defined timestamp stripping affect both WAL replay and recovery flush output.
- `avoid_flush_during_recovery` preserves active WALs instead of flushing everything, which complicates WAL liveness and future deletion.
- Best-efforts recovery ignores normal `CURRENT` assumptions and must still rebuild enough metadata safely.
- Async WAL precreation and async file opening publish background results through shared DB state and must handle shutdown/failure races.
- Dynamic-level trivial moves during open are persisted only if recovery succeeds; incorrect edits can reshape the LSM unexpectedly.
- Persistent stats CF recreation uses normal write paths while open is still in progress, so lock transitions and hidden-handle state matter.

## Test Signals

Important tests include new DB creation and manifest/CURRENT sync, open retry with verify-and-reconstruct reads, best-efforts recovery, direct-I/O compatibility failure, WAL tracking in MANIFEST, missing/extra WAL handling, all WAL recovery modes, WAL filter modify/ignore/stop/corrupt cases, timestamp-size WAL replay, recovered memtable flush with blob additions, `avoid_flush_during_recovery`, PIT dummy write/sync, DB ID/IDENTITY combinations, persistent stats format migration, create-missing-CF open, dynamic-level trivial move migration, async WAL precreate hit/miss/failure, async file-open errors, and crash tests around recovery edit persistence. The file exposes many `TEST_SYNC_POINT` hooks for WAL replay, flush, manifest optimization, async WAL precreate, async open, and final open sequencing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_open.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_readonly.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_readonly.cc

## Purpose

`db_impl_readonly.cc` implements the read-only DB variant. It opens a DB without write ownership, supports point lookups and iterators over recovered versions/memtables, rejects write APIs in the header, and exposes `DB::OpenForReadOnly` entry points. It reuses normal DBImpl recovery in read-only mode but avoids creating writable WALs, flushing, compaction, or file-deletion state changes.

## Important APIs, Types, And Functions

- `DBImplReadOnly::DBImplReadOnly` constructs `DBImpl` with `read_only=true`, `seq_per_batch=false`, and `batch_per_txn=true`.
- `DBImplReadOnly::GetImpl` implements read-only `Get` with timestamp validation, memtable/table lookup, merge handling, optional blob resolution for memtable blob references, and read statistics.
- `DBImplReadOnly::NewIterator` creates a single-CF arena-wrapped DB iterator over a referenced superversion.
- `DBImplReadOnly::NewIterators` creates multiple CF iterators with shared read sequence and carefully unreferences already-acquired superversions on validation failure.
- `OpenForReadOnlyCheckExistence` checks `CURRENT`/MANIFEST existence or creates the directory under historical `create_if_missing` behavior.
- `DB::OpenForReadOnly` overloads handle default-CF and multi-CF open, including a fast attempt to open a fully compacted DB through `CompactedDBImpl::Open`.
- `DBImplReadOnly::OpenForReadOnlyWithoutCheck` constructs the read-only impl, recovers with `read_only=true`, creates handles, installs superversions, marks open success, and optionally schedules async file opening.

## Control Flow

Default-CF `DB::OpenForReadOnly` first checks existence, clears `dbptr`, tries `CompactedDBImpl::Open`, and if that fails builds default column-family descriptors and calls `OpenForReadOnlyWithoutCheck`. The multi-CF overload performs the same existence check and delegates directly.

`OpenForReadOnlyWithoutCheck` clears output handles, creates `DBImplReadOnly`, locks the DB mutex, calls base `Recover(column_families, true, error_if_wal_file_exists)`, validates that requested CFs exist, creates `ColumnFamilyHandleImpl` objects, installs superversions for every recovered CF, sets `opened_successfully_`, schedules async table-file opening if requested, unlocks, cleans the `SuperVersionContext`, and either publishes the DB or deletes handles/impl on failure.

`GetImpl` validates timestamp usage against CF comparator settings, clears output timestamp storage, sets a snapshot sequence to `versions_->LastSequence()`, builds a timestamp read callback, traces the get if tracing is enabled, obtains the current superversion without ref/unref overhead, checks collapsed-history constraints for timestamp reads, probes mutable memtable first, postprocesses blob-backed memtable values when necessary, otherwise probes the current version's files, and records key/byte/perf counters. It supports returning values, wide columns, or merge operands.

`NewIterator` validates `ReadOptions::io_activity`, normalizes unknown activity to `kDBIterator`, validates timestamp settings and collapsed-history constraints, refs the current superversion, chooses the explicit snapshot sequence or last sequence, and creates an arena-wrapped DB iterator with refresh and memtable-flush marking disabled. `NewIterators` applies the same checks across CFs, refs all superversions before constructing iterators, and unwinds refs on failure.

## State And Persistence Behavior

Read-only open reads MANIFEST, WAL files if recovery requires them, and OPTIONS metadata, but it does not create a new WAL or write recovery edits. The base recovery path updates in-memory `versions_`, memtables, `options_file_number_`, handles, and superversions. `GetImpl` reads at `LastSequence()` rather than installing a DB snapshot. Iterators hold superversion references so files/memtables remain alive while the iterator exists. `FlushForGetLiveFiles` is a no-op in the header so live-file listing does not attempt a read-only flush.

## Dependencies And Integration Points

This file depends on normal DBImpl recovery/open infrastructure, `CompactedDBImpl`, column-family handles, superversions, memtables, `Version::Get`, merge context, blob fetcher/cache, timestamp/collapsed-history validation helpers, tracing/perf counters, and async table opening from `db_impl_open.cc`. It is the implementation behind the public `DB::OpenForReadOnly` API.

## Risks And Edge Cases

- `GetImpl` intentionally avoids normal superversion ref/unref for read-only mode; that assumes no background writes/compactions will swap state underneath it.
- Timestamp validation must reject reads without timestamps on timestamp-enabled CFs and mismatched timestamp sizes.
- Read-only recovery with `error_if_wal_file_exists` must detect non-empty WALs to avoid silently exposing unflushed data when the caller asked for strictness.
- Blob-backed memtable values can exist after recovery or option changes, so blob fetcher setup must account for both direct-write and blob-file settings.
- Multi-iterator creation must release all acquired superversion refs if any CF fails collapsed-history validation.
- The fully compacted fast path changes which implementation backs `DB::OpenForReadOnly`, so behavior should remain API-compatible.

## Test Signals

Useful tests include read-only point gets from memtable and SST, merge operand reads, wide-column/entity reads, timestamp-enabled CF reads and collapsed-history failures, blob-backed recovered memtable values, iterator and multi-iterator lifetime/ref cleanup, `io_activity` validation, default and multi-CF open, missing CF errors, `create_if_missing` historical behavior, non-empty WAL rejection with `error_if_wal_file_exists`, async file opening in read-only mode, and fallback from `CompactedDBImpl::Open` to `DBImplReadOnly`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_readonly.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_readonly.h -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_readonly.h

## Purpose

`db_impl_readonly.h` declares `DBImplReadOnly`, the DBImpl subclass used for ordinary read-only opens. It exposes read operations, blocks mutating DB APIs, and provides the helper used by public `DB::OpenForReadOnly` overloads.

## Important APIs, Types, And Functions

- `class DBImplReadOnly : public DBImpl` inherits most read infrastructure from DBImpl.
- Constructor `DBImplReadOnly(const DBOptions&, const std::string&)` and deleted copy/assignment enforce normal DB object ownership.
- `GetImpl`, `NewIterator`, and `NewIterators` are overridden to provide read-only read paths.
- Mutating APIs including `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, `Write`, `CompactRange`, `CompactFiles`, file-deletion controls, `Flush`, `SyncWAL`, `FlushWAL`, external-file ingestion, import, clipping, and column-family creation all return `Status::NotSupported("Not supported operation in read only mode.")`.
- `GetLiveFiles` delegates to `DBImpl::GetLiveFiles` with `flush_memtable=false`, ignoring the caller flush flag.
- `FlushForGetLiveFiles` is overridden as a no-op.
- Private static `OpenForReadOnlyWithoutCheck` centralizes construction/recovery after caller-side existence checks.

## Control Flow

The public DB API routes read-only opens through friend class `DB`, which calls `OpenForReadOnlyWithoutCheck`. Once constructed and recovered, read APIs use the overrides declared here. Write-like APIs fail immediately before they can schedule WAL writes, flushes, compactions, ingestion, metadata updates, or column-family mutations.

## State And Persistence Behavior

The class is designed to avoid persistent mutation. It does not allow writes, WAL sync/flush, manual flush, compaction, ingestion, CF creation, or file deletion toggling. Live-file listing is read-only because memtable flushing is suppressed. Recovery still builds in-memory state and may read WALs to expose the latest persisted data, but the class does not publish new recovery metadata.

## Dependencies And Integration Points

The header depends on `DBImpl` and public RocksDB API types such as `WriteOptions`, `ReadOptions`, `ColumnFamilyHandle`, `Iterator`, compaction options, external-file ingestion types, and import metadata. It integrates with `db_impl_readonly.cc` for read paths and with public `DB::OpenForReadOnly` overloads through the `friend class DB` declaration.

## Risks And Edge Cases

- New mutating DB APIs added to the base class can bypass read-only restrictions unless this class is updated; the header includes a FIXME noting missing write-function overrides.
- `GetLiveFiles` intentionally ignores a caller request to flush; tests should ensure this behavior is not mistaken for a successful flush.
- Public overload hiding is managed with `using` declarations; missing `using` entries can accidentally hide base overloads or change API availability.
- Returning `NotSupported` is the safety contract, so status text/behavior consistency matters for callers that branch on read-only failures.

## Test Signals

Compile/API tests should verify all mutating methods return `NotSupported` in read-only mode, while read methods remain available. Regression tests should check that adding new DB write APIs requires read-only overrides, `GetLiveFiles` never flushes, `FlushForGetLiveFiles` is a no-op, and public overload resolution continues to select the intended read-only methods.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_readonly.h -->

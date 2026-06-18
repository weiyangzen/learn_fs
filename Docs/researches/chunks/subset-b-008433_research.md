# sources/storage-engines/foundationdb/fdbclient/FileBackupAgent.cpp lines 6360-8854

## Scope

This chunk covers the tail of `RestoreDispatchTaskFunc`, restore status/abort helpers, the full-restore startup task, the `FileBackupAgentImpl` control-plane methods for backup/restore submission, waiting, status, pause, and atomic restore, the public `FileBackupAgent` forwarding methods, and a few fast-restore/blob-failure test helpers. Earlier task implementations for reading range/log blocks and applying mutations are outside this chunk, but this range is the orchestration layer that discovers restorable files, creates restore work, records status state, and exposes the public backup/restore API surface.

## Purpose

The code coordinates FoundationDB file backup and restore workflows through the task bucket and persistent `BackupConfig`/`RestoreConfig` metadata. Its main responsibilities are:

- Continue restore dispatch by splitting restore files into block tasks, preserving version-boundary batching so mutation logs are committed only after all range/log blocks for a batch finish.
- Report, wait for, and abort restores by reading restore tags and state keys under system-key and lock-aware transaction options.
- Start a full restore by validating state, forcing the destination cluster's read version above the target restore version, discovering the range/log files needed from the backup container, and persisting file metadata/counts into restore config maps.
- Decide the restore data path after startup: traditional range-file restore, partitioned-log dispatch, or BulkLoad-backed range restoration followed by mutation-log application.
- Submit backups and restores, normalize ranges, validate tag reuse, set up source/destination containers, persist options such as mutation-log type and snapshot mode, and enqueue the initial task.
- Provide user-facing status in text and JSON, including snapshot, mutation log, rangefile, BulkDump/BulkLoad compatibility, pause, lag, and recent error information.
- Implement control operations such as discontinue, abort, wait, pause/resume, worker disable checks, and correctness-only atomic restore.

## Important APIs, Types, and Functions

- `RestoreDispatchTaskFunc::_finish()` tail and `addTask()`:
  - Queues `RestoreRangeTaskFunc` or `RestoreLogDataTaskFunc` per file block.
  - Tracks `beginVersion`, `beginFile`, `beginBlock`, `batchSize`, and `remainingInBatch`.
  - Uses `TaskFuture` joining through `TaskCompletionKey::joinWith(allPartsDone)` so a dispatch batch completes only when all block tasks and any chained dispatch tasks finish.
  - Persists progress with `restore.filesBlocksDispatched().atomicOp(...)` and schedules the next dispatch or completion task.

- Restore helpers in `fileBackup`:
  - `restoreStatus(tr, tagName)` reads all restore tags or a single tag and returns `RestoreConfig::getFullStatus()`.
  - `abortRestore(tr, tagName)` marks runnable restores as `ERestoreState::ABORTED`, clears apply-mutation keys, cancels tag tasks, and unlocks the database.
  - `abortRestore(cx, tagName)` wraps the transactional abort retry loop and then commits a dummy conflict transaction to ensure mutation appliers have stopped submitting writes.

- `StartFullRestoreTaskFunc`:
  - `_execute()` validates `ERestoreState::QUEUED`/`STARTING`, clears stale file counters/maps, opens the backup container via `getBackupContainerWithProxy()`, discovers `RestorableFileSet`, writes log/range/all-file entries in transaction-sized chunks, and stores `firstConsistentVersion`.
  - `_finish()` transitions to `RUNNING`, initializes apply-mutation begin/end versions, chooses BulkLoad, partitioned-log, or standard dispatch, initializes incremental restore apply maps, and finishes the startup task.
  - `addTask()` binds a `RestoreConfig` UID to a `restore_start` task.

- `FileBackupAgentImpl`:
  - `waitBackup()` watches backup state until it is not runnable, or until differential mode is reached when `StopWhenDone` is false.
  - `submitBackup()` validates duplicate/runnable tags, enforces partitioned-log and range-partitioned-log mutual exclusion, creates the backup container, normalizes ranges, sets mutation-sharing destination UID metadata, persists `BackupConfig`, and enqueues `StartFullBackupTaskFunc`.
  - `submitRestore()` normalizes restore ranges, rejects duplicate/runnable restore tags, checks destination emptiness for traditional non-log-only restores, creates `RestoreConfig`, initializes mutation application, enqueues `StartFullRestoreTaskFunc`, and locks or verifies the database lock.
  - `waitRestore()` watches restore state and optionally prints progress every second while runnable.
  - `discontinueBackup()` either cancels an already restorable backup and marks it `STATE_COMPLETED`, or sets `stopWhenDone`.
  - `abortBackup()` cancels tasks, erases log data, clears backup start ID, and marks the config `STATE_ABORTED`.
  - `checkAndDisableBackupWorkers()` and `checkAndDisableRangeBackupWorkers()` disable worker roles when no matching partitioned backup remains.
  - `changePause()` writes both the task-bucket pause key and `backupPausedKey`.
  - `getStatusJSON()` and `getStatus()` build machine-readable and human-readable backup status.
  - `restore()` validates backup description/encryption, resolves target versions, verifies `getRestoreSet()`, submits restore, and optionally waits for completion.
  - `atomicRestore()` locks the source at a commit version, waits for the running backup to become restorable at or after that version, stops the backup, clears target ranges, and restores from the same backup URL under the same lock UID.

- Public `FileBackupAgent` methods:
  - `restore()` overloads adapt single-range, multi-range, and per-range begin-version arguments into `FileBackupAgentImpl::restore()`.
  - `atomicRestore()`, `abortRestore()`, `restoreStatus()`, `waitRestore()`, `submitBackup()`, `discontinueBackup()`, `abortBackup()`, status methods, `getLastRestorable()`, `setLastRestorable()`, `waitBackup()`, and `changePause()` forward into the implementation or `fileBackup` helpers.
  - `dataFooterSize` is defined as `20`.

- Test/support helpers:
  - `LogInfo` stores async log file metadata and an offset.
  - `insideValidRange()` checks whether a test key-value belongs to backup and restore ranges and logs trace details.
  - `writeKVs()` writes a slice of key-values and reads it back as a sanity check.
  - `simulateBlobFailure()` injects buggified blob-related failures such as HTTP request, connection, timeout, or lookup errors.

## Control Flow

Restore dispatch continues from previously loaded `RestoreConfig::fileSet()` entries. For each restore file, the dispatcher calculates block offsets from `beginBlock * blockSize`, queues a block task for range files or log files, and advances `beginBlock`, `blocksDispatched`, and `remainingInBatch`. If it finishes a file, it advances `beginFile` by appending `'\x00'` so later range scans resume after that file. If no blocks are dispatched, it either doubles `batchSize` when the queried files are too sparse/empty or chains another dispatch task into the existing batch future. When blocks were dispatched, it increments persistent block-dispatch counters, forces `remainingInBatch >= 1` if stopped mid-version, and schedules either an immediate same-batch dispatch or a follow-on dispatch that waits for `allPartsDone`.

Restore startup has an execute/finish split. `_execute()` first commits the state transition to `STARTING`, then separately ensures the destination read version exceeds `restoreVersion` by writing `minRequiredCommitVersionKey` as needed. It asks the backup container for a `RestorableFileSet`, converts range and log metadata into `RestoreConfig::RestoreFile` records, computes `firstConsistentVersion`, and writes log-file, range-file, and combined file maps in chunks capped around 1 MB of transaction payload. `_finish()` then switches the restore to `RUNNING`, initializes apply-mutation versions, and chooses downstream work: BulkLoad restore plus log dispatch when `useRangeFileRestore` is false, partitioned restore dispatch for `MutationLogType::PARTITIONED_LOG`, or normal `RestoreDispatchTaskFunc`.

Backup submission is a single transactional setup path. It rejects active duplicate tags, removes old non-runnable config, checks mutation-log-type conflicts, creates or opens the destination container, normalizes backup ranges through `KeyRangeMap`, assigns mutation-sharing destination UID metadata, persists config fields, points the tag to the new UID, and schedules the first full-backup task. Restore submission follows the same tag/config pattern but also validates destination emptiness for traditional restores, initializes apply-mutation prefix handling, and locks or validates the database lock using the restore UID.

Waiting and status paths are watch-driven. `waitBackup()` watches `BackupConfig::stateEnum().key`; `waitRestore()` watches `RestoreConfig::stateEnum().key`, with optional progress printing and a one-second delay race for verbose output. Status generation performs one retryable read transaction, collects version/timestamp information through timekeeper helpers, and formats either JSON fields or CLI text.

Atomic restore is a correctness workflow: require the backup to be in `STATE_RUNNING_DIFFERENTIAL`, lock the database and capture the lock commit version, wait until the backup has a latest restorable version at least that high, discontinue and wait for the backup to stop, clear target ranges, then invoke the normal restore path using the backup container URL and the same lock UID.

## State and Persistence Behavior

- Restore task parameters persist in task metadata: `beginVersion`, `beginFile`, `beginBlock`, `batchSize`, `remainingInBatch`, and `StartFullRestoreTaskFunc::Params::firstVersion`.
- Restore config state includes `stateEnum`, `restoreVersion`, `firstConsistentVersion`, `beginVersion`, `onlyApplyMutationLogs`, `inconsistentSnapshotOnly`, `unlockDBAfterRestore`, `mutationLogType`, `useRangeFileRestore`, `sourceContainer`, restore ranges, apply-mutation prefixes/maps, batch future key, file maps, and counters such as file count, file-block count, and blocks dispatched.
- File discovery persists three views: `logFileSet()`, `rangeFileSet()`, and combined `fileSet()`. The combined map drives dispatch ordering; the specialized maps preserve log/range metadata for other restore behavior.
- Backup config state includes tag, state enum, backup container, stop-when-done flag, normalized ranges, snapshot intervals, mutation log type, incremental-only flag, snapshot mode, destination UID value, latest-version metadata, byte counters, error maps, BulkDump job ID, and BulkDump progress integration.
- Tag state is stored via `KeyBackedTag` mappings from user tags to `{ UID, aborted flag }`. Both backup and restore submission replace tag pointers only after validating old runnable state.
- Database lock state is part of restore correctness. Normal restore may lock or verify a lock by UID; abort unlocks using the restore UID; atomic restore reuses a generated UID across lock, optional system restore, user restore, and final unlock.
- Worker pause state is duplicated intentionally: the task bucket pause key controls backup-agent tasks, while `backupPausedKey` controls backup workers.
- `lastRestorable` is stored under a `FileBackupAgent` keyspace by tag and encoded as a `Version`.

## Dependencies and Integration Points

- FoundationDB transaction APIs: `ReadYourWritesTransaction`, `Transaction`, `runRYWTransaction`, transaction options for system keys, lock-aware reads/writes, immediate priority, and commit-on-first-proxy.
- Task infrastructure: `TaskBucket`, `FutureBucket`, `Task`, `TaskFuture`, `TaskCompletionKey`, `REGISTER_TASKFUNC`, task priorities, task cancellation through tags, and `keepRunning()` leases.
- Backup container APIs: `IBackupContainer::openContainer()`, `create()`, `describeBackup()`, `getRestoreSet()`, `getURL()`, `getProxy()`, encryption block-size handling, and proxy wrapping.
- Restore/backup config wrappers: `RestoreConfig`, `BackupConfig`, key-backed tags/maps/sets, range maps, and helpers such as `getAllRestoreTags()`, `makeRestoreTag()`, `makeBackupTag()`, `krmSetRange()`, and `eraseLogData()`.
- BulkLoad/BulkDump integration: `BulkLoadRestoreTaskFunc::addTask()`, `getBulkLoadMode()`, `originalBulkLoadMode()`, `bulkDumpJobId()`, `getBulkDumpProgress()`, `BulkDumpProgress`, and snapshot modes `rangefile`, `bulkdump`, and `both`.
- Mutation-log worker integration: `MutationLogType`, partitioned/range-partitioned backup detection, `enable/disable` worker helpers, `backupPartitionRequiredKey`, and dispatch variants for partitioned logs.
- Time/status integration: timekeeper version-to-epoch helpers, formatting helpers for durations, bytes, timestamps, versions, JSON builders, and trace events.
- CLI/user workflows integrate through public `FileBackupAgent` methods used by `fdbbackup`/`fdbrestore`, including wait/verbose behavior and printed error messages for encryption, destination, and container failures.

## Risks and Edge Cases

- Restore batching must not end mid-version when range files and log files overlap a version. The `beginFile`/`remainingInBatch` logic is the main guard; an error here can allow logs to apply before all snapshot/range blocks for the same version finish.
- Sparse or empty restore files can cause no block tasks to be dispatched. The code doubles `batchSize` when no files were consumed and otherwise treats it as empty-file progress, avoiding a tight loop but risking very large batches if metadata is unexpectedly sparse.
- `StartFullRestoreTaskFunc::_execute()` writes large file lists in approximately 1 MB chunks, but comments note that very large file sets can still stress value/transaction limits because file-set metadata can be large.
- BulkLoad restore intentionally skips destination-empty checks because DD range-lock overwrite is expected. Incorrectly selecting `useRangeFileRestore=false` could overwrite existing ranges that traditional restore would reject.
- Encryption validation is strict: encrypted backups require a key file, and unencrypted backups reject a provided key file. Container caching requires explicitly resetting the encryption block size after reopening.
- Blobstore backup description uses `invalidVersion` to tolerate eventually consistent metadata. Restore version validation still depends on `getRestoreSet()` returning a complete set.
- Backup mutation-log types `PARTITIONED_LOG` and `RANGE_PARTITIONED_LOG` are mutually exclusive at submission time because worker recruitment depends on active non-default type.
- Status JSON currently builds error objects but does not push them into `errorList` in the shown code, so JSON `Errors` may remain empty even when errors were read.
- Atomic restore assumes a running differential backup, waits by polling every 0.2 seconds for a restorable version, and clears destination ranges before normal restore; failures after clearing but before restore completion leave the database locked/cleared until higher-level recovery handles it.
- `writeKVs()` assumes `begin` is valid when reading `kvs[begin]`; callers must not pass an out-of-range empty slice except the code only tolerates `begin == end` after forming the range.
- `simulateBlobFailure()` injects random transient errors only under `buggify()`, so tests must tolerate nondeterministic failure paths in simulation.

## Test Signals

- Restore dispatch: files with zero size, multiple blocks, mid-file continuation, mid-version stopping, overlapping range/log versions, batch-size exhaustion, `RESTORE_DISPATCH_ADDTASK_SIZE` under buggify, and `filesBlocksDispatched` increments.
- Restore lifecycle: status on no tags, status on all tags, abort of missing/runnable/non-runnable restores, clearing apply-mutation keys, task cancellation, unlock behavior, and dummy transaction after abort.
- Full restore startup: queued-to-starting transition, unexpected old state error logging, destination version forcing via `minRequiredCommitVersionKey`, missing restore data, logs-only restore, inconsistent-snapshot-only restore, first-consistent-version calculation, and transaction chunking for large file metadata sets.
- Restore path selection: BulkLoad restore creates a `BulkLoadRestoreTaskFunc`, persists original BulkLoad mode, switches to log-only dispatch after BulkLoad, partitioned-log dispatch uses version batches, and traditional restore queues normal dispatch.
- Backup submission: duplicate active tag rejection, old completed config clearing, local `file://` URL timestamp suffixing, container create failure, last-backup timestamp in the future, range normalization/coalescing, mutation-sharing UID reuse, snapshot mode persistence, and partitioned/range-partitioned conflict messages.
- Restore submission: duplicate UID/tag handling, destination-not-empty rejection for traditional restore, validation-prefix exception, BulkLoad destination precheck skip, restore range prefix assertions, lock versus check-lock paths, begin-version persistence, and apply-mutation initialization.
- Waiting and status: watch wakeups on backup/restore state changes, verbose restore progress cadence, paused agent reporting, text/JSON snapshot modes, BulkLoad compatibility, BulkDump progress/stalled task fields, lag calculations, and recent versus older error grouping.
- Backup controls: discontinue before/after latest restorable version exists, `stopWhenDone` duplicate behavior, abort cleanup of log data and backup start ID, worker-disable calls when no partitioned backups remain, and range-partition cleanup marker write.
- Atomic restore: requires `STATE_RUNNING_DIFFERENTIAL`, captures a lock commit version, waits for restorable version to catch up, handles discontinue races, clears requested ranges, and restores with the same lock UID.
- Public wrappers: overload behavior for default backup ranges, per-range versus uniform begin versions, optional lock UID generation, `setLastRestorable()` encoding, and forwarding consistency for backup/restore status/control methods.

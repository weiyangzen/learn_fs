# sources/storage-engines/foundationdb/fdbclient/FileBackupAgent.cpp lines 1-6359

## Scope

This chunk covers the front and middle of FoundationDB's file backup agent implementation. It starts with helper state, restore configuration, backup file encoders/decoders, legacy backup abort compatibility, snapshot/log backup task functions, BulkDump snapshot integration, BulkLoad restore integration, range-file restore blocks, old-format mutation-log restore, partitioned-log conversion, and the beginning of non-partitioned restore dispatch. The requested range ends inside `RestoreDispatchTaskFunc::_finish()` at the point where it begins iterating restore files for a dispatch batch; the remainder of that task and the public `FileBackupAgent` wrapper methods are outside this chunk.

## Purpose

The code implements the task-bucket workflows that turn a FoundationDB backup configuration into external backup-container files and later restore those files back into a database. It supports three major data paths:

- Traditional range-file snapshots plus copied mutation-log files.
- Backup-worker partitioned logs, including restore-time merging of per-tag log streams into old backup mutation format.
- New BulkDump/BulkLoad snapshot acceleration, where snapshots are delegated to the BulkDump subsystem and restored through BulkLoad before mutation-log replay.

The implementation is actor-heavy and intentionally splits long-running work into durable `TaskBucket` tasks. Each task has an execute phase for external I/O or multi-transaction work and a finish phase for small, durable state updates.

## Important APIs, Types, and Functions

- Top-level helpers:
  - `monitorBulkDumpJobCompletion()` polls `getSubmittedBulkDumpJob()` until the submitted BulkDump job disappears or a timeout expires.
  - `verifyBulkDumpDatasetCompleteness()` verifies a `bulkdump_data/<job-id>/` directory exists and has files for filesystem backup containers.
  - `getBulkLoadTaskProgress()` scans `bulkLoadTaskPrefix` range-map entries, counts BulkLoad tasks by phase, and totals manifest bytes.
  - `monitorBulkLoadJobCompletionWithProgress()` polls a running BulkLoad job and periodically persists restore counters such as finished blocks, submitted/triggered/running tasks, total tasks, and bytes written.

- Restore configuration:
  - `RestoreConfig` extends `KeyBackedTaskConfig` under `fileRestorePrefixRange` and stores restore state, prefix translation, restore ranges, source container, versions, progress counters, file sets, BulkLoad flags, and apply-mutations coordination keys.
  - `RestoreConfig::RestoreFile` is the durable file descriptor ordered by `version` and `fileName`; it records whether a file is a range file or log file, block/file sizes, log end version, and partitioned-log tag metadata.
  - `getRestoreRangesOrDefault()` reads the newer `restoreRangeSet()` and falls back to older `restoreRanges()`/`restoreRange()` properties for compatibility.
  - `getProgress_impl()` and `getFullStatus_impl()` render restore status and add BulkLoad-specific phase details when `useRangeFileRestore` is false.

- File format support:
  - `fileBackup::RangeFileWriter` writes snapshot range blocks with a version header, begin/end keys, duplicated boundary KVs around block splits, and `0xff` padding.
  - `decodeRangeFileBlock()` and `decodeKVPairs()` validate headers, decode range-file blocks, and reject non-`0xff` trailing padding.
  - `fileBackup::LogFileWriter` writes old mutation-log blocks with `BACKUP_AGENT_MLOG_VERSION` headers and padded key/value records.
  - `decodeMutationLogFileBlock()` reads those log blocks for restore.
  - `getBackupContainerWithProxy()` reopens a backup container with the global `fileBackupAgentProxy`.

- Partitioned-log iterators:
  - `TwoBuffers` asynchronously pipelines fixed-size file reads across two buffers.
  - `PartitionedLogIteratorSimple` and `PartitionedLogIteratorTwoBuffers` read new partitioned-log backup files, skip block headers/padding, decode `VersionedMutation` records, and hide overlap between adjacent log files using stored end-version boundaries.
  - `endOfBlock()` treats `0xff` as block padding.

- Backup tasks:
  - `BackupRangeTaskFunc` writes snapshot range files for shard ranges, updates `snapshotRangeFileMap`, and recursively splits work on shard boundaries.
  - `BackupSnapshotDispatchTask` builds a shard map, subtracts already-dispatched ranges and out-of-backup ranges, dispatches range tasks according to snapshot schedule, and then either schedules another dispatch or `BackupSnapshotManifest`.
  - `BackupSnapshotManifest` walks the completed range-file map backwards to produce a non-overlapping snapshot manifest file and updates snapshot completion versions.
  - `BackupLogRangeTaskFunc` waits until its end version is readable, reads backup mutation-log key ranges, writes old-format log files, and splits large version spans.
  - `BackupLogsDispatchTask` advances continuous log backup, updates last restorable versions, dispatches log-copy tasks, erases old backup-log data, or polls when partitioned log modes are used.
  - `FileBackupFinishedTask` erases remaining log data, clears `backupStartedKey`, and marks a cleanly stopped backup completed.
  - `BulkDumpTaskFunc` submits or attaches to a BulkDump job, writes BulkDump snapshot metadata into the backup container, and persists `bulkDumpJobId`/BulkDump snapshot versions.
  - `StartFullBackupTaskFunc` enables backup workers if needed, records a begin version, starts mutation logging, initializes a snapshot, and schedules snapshot/log/finalization tasks according to snapshot mode.

- Restore tasks:
  - `BulkLoadRestoreTaskFunc` finds a BulkDump job id from task params or snapshot metadata, verifies the dataset, enables BulkLoad mode, submits a BulkLoad job, monitors it with progress, and marks the BulkLoad snapshot phase complete.
  - `RestoreCompleteTaskFunc` marks restore completed, bumps the metadata version, clears large restore maps, clears apply-mutation keys, and optionally unlocks the database.
  - `RestoreRangeTaskFunc` reads one range-file block, intersects it with requested restore ranges, applies prefix translation, clears/replaces target KV ranges, increments byte counters, and records original file ranges in the apply-mutations range map.
  - `RestoreLogDataTaskFunc` reads old-format log blocks, filters mutations against restore ranges, writes them under the restore `alog` prefix, and increments block/byte progress.
  - `RestoreLogDataPartitionedTaskFunc` groups partitioned log files by tag, merges per-tag iterators by commit version, converts new-format `VersionedMutation` records into old backup mutation KVs, and writes them under the restore mutation-log prefix.
  - `RestoreDispatchPartitionedTaskFunc` dispatches version batches for partitioned restore, including range-file block tasks, one partitioned-log conversion task, and the next dispatch task.
  - `RestoreDispatchTaskFunc` starts the non-partitioned dispatch state machine; in this chunk it handles apply-lag gating, empty-file completion decisions, batch future creation, and starts iterating files for block dispatch.

## Control Flow

Backup start begins with `StartFullBackupTaskFunc::_execute()`, which determines mutation log type, enables partitioned or range-partitioned backup workers, records the read version, and updates `backupStartedKey` so backup workers know the backup UID and begin version. Its finish phase starts default mutation logging for non-partitioned backups, creates encryption metadata in the backup container, sets the backup state to running, initializes snapshot metadata, and schedules the selected snapshot path plus continuous log dispatch and final cleanup.

Traditional snapshots flow from `BackupSnapshotDispatchTask` into many `BackupRangeTaskFunc` tasks. Dispatch constructs a `KeyRangeMap` of current shard boundaries, marks completed ranges from `snapshotRangeDispatchMap`, skips ranges outside `backupRanges`, calculates how many shards should have been dispatched by the next snapshot interval, and adds random not-done shard ranges to the task bucket. It deliberately avoids marking a snapshot finished in the same iteration that dispatched the final batch. Finish clears batch state, sets the dispatch-done future, and either schedules another dispatch at `nextDispatchVersion` or schedules `BackupSnapshotManifest` after the batch future.

`BackupRangeTaskFunc::_execute()` first splits itself if its input contains shard boundaries. Otherwise it streams committed KVs for its shard range through `readCommitted()`, writes one or more range files at read-version boundaries, and calls `finishRangeFile()` after each file. `finishRangeFile()` makes file creation durable by committing the range slice into `snapshotRangeFileMap`, updating byte/file counters, and advancing the task's begin key so retries continue from the correct point.

Mutation-log backup flows through `BackupLogsDispatchTask`. Each finish invocation advances `latestLogEndVersion`, updates last-restorable state, and either stops if `stopWhenDone` and restorable, schedules a `BackupLogRangeTaskFunc` plus the next dispatch task, or just polls when the backup is using partitioned logs. `BackupLogRangeTaskFunc` waits until the cluster read version exceeds its end version, optionally splits large log-range spans, copies backup-log records into a backup-container log file, and records file size so finish can add it to `logBytesWritten`.

BulkDump backup is a sibling snapshot path. `BulkDumpTaskFunc::_execute()` reads backup ranges and container URL, restores the original BulkDump mode from persisted config, attaches to an already submitted BulkDump job when present, otherwise enables BulkDump mode, creates a job rooted under `bulkdump_data`, submits it, and sets owner metadata. On success it verifies files exist under the job directory, writes a keyspace snapshot file containing BulkDump metadata rather than range files, restores BulkDump mode, and increments the test counter. Finish persists `latestSnapshotEndVersion`, `bulkDumpSnapshotEndVersion`, and `bulkDumpJobId`; in mode `BOTH` it avoids setting `firstSnapshotEndVersion` so range-file completion remains required before restorable state.

BulkLoad restore is a pre-log-replay snapshot path. `BulkLoadRestoreTaskFunc::_execute()` opens the backup container, reads restore ranges, discovers a missing `bulkDumpJobId` by scanning snapshot JSON metadata, verifies the BulkDump dataset, constructs a BulkLoad job for `normalKeys`, registers the BulkLoad range-lock owner, persists/restores the original BulkLoad mode, submits the job lock-aware because restore holds a database lock, and monitors completion while updating progress counters. Missing or incomplete BulkDump data is treated as permanent restore failure and sets restore state to aborted. Finish marks `bulkLoadComplete`, forces block progress counters to total, sets `firstConsistentVersion` if absent, signals its future, and finishes the task.

Range-file restore dispatches one `RestoreRangeTaskFunc` per block. Each block decode yields begin/end boundary keys plus real KVs. The task intersects the block range with every requested restore range, applies remove/add prefix mapping, clears the translated subrange, writes KVs with no write-conflict ranges, checks the restore database lock, and records bytes written. Finish maps the original backed-up key ranges to the snapshot version in `applyMutationsMapPrefix()` so later mutation application can tell which keys have a snapshot baseline.

Old-format log restore uses `RestoreLogDataTaskFunc`. It decodes a log block, groups multi-part mutation chunks by version with `AccumulatedMutations`, filters complete groups whose mutations do not intersect the target restore ranges, writes the remaining chunks under `restore.mutationLogPrefix()`, and lets the apply-mutations machinery consume them later. Partitioned-log restore instead uses `RestoreLogDataPartitionedTaskFunc`, which creates one iterator per tag, repeatedly finds the minimum next version, gathers all tag mutations for that version, converts them to old backup mutation KVs with `generateOldFormatMutations()`, batches by byte size, and writes to the same mutation-log prefix.

`RestoreDispatchPartitionedTaskFunc` advances version batches. It sets the apply end version for the previous batch, waits if apply lag is too high, gathers relevant log and range files for the next batch, queues all range-file block tasks, queues one partitioned-log conversion task, and schedules the next batch after the batch future. If it passes the restore version, it either schedules restore completion or requeues itself until apply lag reaches zero.

The non-partitioned `RestoreDispatchTaskFunc` follows the same batch principle. In the covered range it updates apply end version at batch boundaries, backs off on large apply lag, creates or reuses the batch future, handles empty-file cases by scheduling completion or a final apply-to-restore-version task, and begins the per-file loop that dispatches range/log blocks. The body after line 6359 is outside this chunk.

## State and Persistence Behavior

Durable state is primarily stored through `BackupConfig`, `RestoreConfig`, `TaskBucket`, and `FutureBucket` key-backed structures under system-key prefixes. Tasks carry config UIDs and task parameters, while completion dependencies are represented by future keys. Most execute phases do file I/O and multi-transaction work; finish phases commit small state transitions and set futures.

Backup state includes:

- Tag-to-UID mappings and abort flags through `KeyBackedTag`.
- `BackupConfig` fields such as backup ranges, destination UID, backup container, mutation log type, `stateEnum`, snapshot interval/version fields, snapshot dispatch maps, range-file map, log and range byte counters, last snapshot/log end versions, restorable version state, snapshot mode, BulkDump job id, original BulkDump mode, and worker-start markers.
- Cluster-level backup worker state through `backupStartedKey` and `backupPartitionRequiredKey`.
- Backup-container persistence through range files, log files, keyspace snapshot manifests, encryption metadata, and BulkDump metadata.

Restore state includes:

- `RestoreConfig` fields for restore UID/tag, source container URL/object, restore ranges, add/remove prefixes, restore target versions, first consistent version, batch future, progress counters, file sets, `applyMutationsBeginRange`/`applyMutationsEndRange`, `applyMutationsMapPrefix`, BulkLoad flags, original BulkLoad mode, and `unlockDBAfterRestore`.
- Range restore writes directly to user keyspace after clearing the target subrange, while log restore writes backup mutation chunks to the restore `alog` prefix for commit proxies to apply.
- `RestoreCompleteTaskFunc` clears large file/apply maps after completion and bumps `metadataVersionKey` to force clients to notice restored metadata changes.

Idempotence is an important design property. Range snapshot tasks persist begin-key advancement only after finishing a file. Restore block tasks use deterministic clear/set ranges and task futures. BulkDump and BulkLoad modes are persisted before task creation so retry after process failure can restore the previous DD mode. Existing BulkDump jobs are reused rather than blindly submitting duplicate jobs.

## Dependencies and Integration Points

- FoundationDB task framework: `TaskBucket`, `FutureBucket`, `TaskFuncBase`, `REGISTER_TASKFUNC`, task validation, task futures, scheduled versions, and task priorities.
- Key-backed configuration: `KeyBackedTaskConfig`, `KeyBackedProperty`, `KeyBackedSet`, `KeyBackedBinaryValue`, `krmSetRange()`, and `krmGetRanges()`.
- Backup container APIs: `IBackupContainer`, `BackupContainerFileSystem`, `IBackupFile`, `IAsyncFile`, keyspace snapshot files, encryption metadata, range/log file creation, file listing, and snapshot JSON metadata.
- Backup worker / mutation log APIs: `startMutationLogs()`, `eraseLogData()`, `getLogRanges()`, `backupStartedKey`, `enableBackupWorker()`, `enableRangeBackupWorker()`, partitioned log file metadata, and commit-proxy apply-mutations integration.
- BulkDump/BulkLoad APIs: `BulkDumpState`, `BulkLoadJobState`, `createBulkDumpJob()`, `submitBulkDumpJob()`, `getSubmittedBulkDumpJob()`, `setBulkDumpMode()`, `setBulkDumpOwner()`, `createBulkLoadJob()`, `submitBulkLoadJob()`, `getRunningBulkLoadJob()`, `setBulkLoadMode()`, `registerRangeLockOwner()`, `BulkLoadTaskState`, and `BulkLoadManifest` byte counts.
- Database management and locking: `ReadYourWritesTransaction`, system-key and lock-aware transaction options, `checkDatabaseLock()`, `unlockDatabase()`, `lockDatabase` expectations outside this chunk, `metadataVersionKey`, and DD/server-side mode knobs.
- Flow runtime: actors, `Future`, `PromiseStream`, `FlowLock`, `delay()`, `yield()`, `TraceEvent`, `buggify()`, and simulation-only failure/padding behavior.

## Risks and Edge Cases

- BulkLoad/BulkDump mode toggles are global DD-level state. The code persists original mode and restores it on success/error, but concurrent jobs or agents can still create ownership and mode-race hazards; BulkDump explicitly attaches to an existing job to reduce duplicate-submit conflicts.
- `verifyBulkDumpDatasetCompleteness()` only works for `BackupContainerFileSystem` and only checks that the job directory has files. It does not parse manifests, validate shard completeness, or support containers without listing.
- BulkLoad restore lacks client-side validation for server-side prerequisites such as SST ingestion support, shard-location metadata, and read-lock support. The code comments note that missing prerequisites can leave restores running with `0/0` tasks.
- Snapshot mode `BOTH` has subtle restorable-version semantics. `BulkDumpTaskFunc::_finish()` must not set `firstSnapshotEndVersion`; otherwise the backup can appear restorable before the range-file snapshot completes.
- Range-file and log-file formats rely on strict block sizing and `0xff` padding. Corrupted padding, short reads, unsupported file versions, or too-small block sizes raise restore/backup errors.
- Prefix translation during restore has boundary special cases around `allKeys.end` and `strinc(removePrefix)`. Incorrect handling can clear or write outside the intended translated range.
- Mutation-log filtering must keep incomplete multi-chunk mutation groups even if the visible partial data does not match a restore range; otherwise later chunks could be lost.
- Partitioned-log restore assumes per-tag files are continuous enough and versions advance monotonically. It logs severe events for missing tag IDs or non-continuous files, and iterator overlap skipping depends on correct file end-version metadata.
- Restore dispatch intentionally gates on apply lag. If commit proxies do not drain the restore `alog` prefix, dispatch tasks repeatedly requeue and restoration stalls.
- `RestoreDispatchTaskFunc` is split by this chunk boundary; analysis of actual non-partitioned per-file block dispatch, file-set cursor advancement, and subsequent task scheduling requires the next chunk.

## Test Signals

- BulkDump backup: submitting a BulkDump snapshot, reusing an already running job, restoring original BulkDump mode after success/error, writing BulkDump snapshot metadata, persisting `bulkDumpJobId`, rejecting empty/missing dataset directories, and `g_bulkDumpTaskCompleteCount` increments.
- BulkLoad restore: discovering `bulkDumpJobId` from snapshot metadata, aborting permanently when BulkDump metadata or files are missing, submitting a lock-aware BulkLoad job, updating submitted/triggered/running/total progress, restoring BulkLoad mode on timeout/error, marking `bulkLoadComplete`, and `g_bulkLoadRestoreTaskCompleteCount` increments.
- Backup snapshot dispatch: shard-map construction, backup-range skipping, already-dispatched range coalescing, randomized shard dispatch, `snapshotBatchFuture` cleanup, not finishing in the same iteration as final dispatch, and manifest generation after all shard tasks finish.
- Range file backup/restore: block-boundary duplication, padding validation, empty-range suppression, range-file map updates, restore clear/set batching, transaction-too-large backoff, original range-to-version map updates, and prefix translation at end boundaries.
- Log backup/restore: delayed reads until `endVersion` is readable, splitting large log spans, log byte accounting, old-format log block decode, mutation chunk completeness checks, range-based log filtering, and writes under restore mutation-log prefix.
- Partitioned restore: two-buffer iterator behavior across file/block boundaries, overlap skipping, per-tag merge ordering, old-format mutation generation by subsequence, apply-lag backoff, byte/block progress accounting, and batch chaining to restore completion.
- Compatibility and error handling: legacy 5.0/5.1 abort task aliases, unsupported task-version rejection, task validation failures, backup worker enablement for partitioned/range-partitioned logs, `backupStartedKey` cleanup, database lock checks during restore writes, and final database unlock behavior.

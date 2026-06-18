# Research: subset-b-008488

## sources/storage-engines/foundationdb/fdbserver/workloads/AtomicOps.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AtomicOps.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AtomicOps.cpp

Purpose: defines the `AtomicOps` simulation workload, a concurrent stress test for FoundationDB atomic mutations. It seeds grouped `ops` keys, runs many clients issuing random atomic mutations, logs the intended mutation operands in ordinary keys, and checks that applying the same atomic operation to the log stream matches the values materialized by the storage engine.

Important APIs, types, and functions: `AtomicOpsWorkload` extends `TestWorkload` and registers through `WorkloadFactory<AtomicOpsWorkload>`. Constructor options include `testDuration`, `transactionsPerSecond`, `actorsPerClient`, `opType`, and `nodeCount`; `opType=-1` selects a random atomic mutation among `Min`, `And`, `ByteMin`, `ByteMax`, `Or`, `Max`, `Xor`, and `AddValue`. `randomValue()` generates operation-specific operands and preserves old API-version behavior for `Min` and `And` when `apiVersion500` is selected. `logDebugKey()` binds each operation number to `log...` and `debug...` keys. `_setup()`, `atomicOpWorker()`, `_check()`, `dumpLogKV()`, `dumpDebugKV()`, `dumpOpsKV()`, and `validateOpsKey()` are the key actors/helpers.

Control flow: client 0 clears stale `log` data and initializes 100 operation groups with `ops%08x%08x` keys. `start()` launches `actorCount` workers per client and returns after `testDuration`. Each worker paces itself with `poisson`, chooses a group and node, writes a debug mapping from operation key to log key, writes the operand to a log key, calls `tr.atomicOp()` against the selected `ops` key, commits, and increments `opNum`. It tolerates `commit_unknown_result` by advancing and relying on the debug/log records to diagnose ambiguity. `_check()` scans each group, replays all logged operands into `xlogResult`, atomically combines all `ops` values into `xopsResult`, compares the two, and performs an explicit summed comparison for `AddValue`.

State and persistence behavior: the workload persists test state under normal user keys: `ops` contains database-applied atomic results, `log` contains committed operand records, and `debug` links operation keys to log records. It also writes scratch keys `xlogResult` and `xopsResult` during checking. There is no external durable state beyond the database; all actor state such as `opNum` and random choices is in memory.

Dependencies and integration points: depends on `NativeAPI.actor.h`, `ReadYourWrites.h`, `TesterInterface.h`, `BulkSetup.h`, Flow actors, `MutationRef` atomic op semantics, `CLIENT_KNOBS->TOO_MANY`, and simulation trace severities. It integrates with the tester through the workload factory and with API-version compatibility by optionally selecting API 500 behavior.

Risks and edge cases: correctness depends on using identical atomic op semantics for the replay path and the database path. Unknown commits may create debug/log patterns that are hard to interpret, and the workload emits diagnostic dumps rather than proving exactly which side committed. `validateOpsKey()` can only require exact per-key equality in single-actor mode because concurrent atomic operations intentionally combine multiple operands. Range scans may hit transaction limits if `nodeCount`, actor count, or runtime is made too high.

Test signals: severe trace events include `LogMismatch`, `LogAddMismatch`, `InconsistentOpsKeyValue`, `MissingOpsKey2`, and range-limit diagnostics. A successful run has `_check()` return true for client 0 after replaying every group.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AtomicOps.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/AtomicOpsApiCorrectness.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AtomicOpsApiCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AtomicOpsApiCorrectness.cpp

Purpose: defines `AtomicOpsApiCorrectness`, a focused API-level correctness workload for individual atomic operations. It checks how each atomic mutation behaves on existing keys, missing keys, empty values, read-your-writes visibility, and legacy API version 500 semantics.

Important APIs, types, and functions: `AtomicOpsApiCorrectnessWorkload` extends `TestWorkload`; `opType` selects the operation under test and `testFailed` reports check status. Shared helper actors include `testAtomicOpSetOnNonExistingKey()`, `testAtomicOpUnsetOnNonExistingKey()`, `testAtomicOpOnEmptyValue()`, `testAtomicOpApi()`, and `testCompareAndClearAtomicOpApi()`. Operation-specific actors are `testMin`, `testMax`, `testAnd`, `testOr`, `testXor`, `testAdd`, `testCompareAndClear`, `testByteMin`, and `testByteMax`.

Control flow: `start()` dispatches exactly one operation test, or randomly chooses one if `opType=-1`. Each helper clears or seeds a key, commits a transaction containing an atomic operation, waits briefly, then reads the key in a separate transaction and in a same-transaction read-your-writes path. Numeric helpers compare little-endian `uint64_t` values; byte helpers compare `StringRef` byte ordering; compare-and-clear expects the key to disappear when absent or equal and remain when unequal. If an unexpected value appears, the helper logs a `SevError` trace and sets `testFailed`.

State and persistence behavior: test keys are deterministic per client (`test_key_*_<clientId>`). The workload mutates only those user keys and clears/reuses them between cases. No metadata or external persistence is involved. For current API behavior, atomic operations on absent keys generally initialize from or preserve the operand according to the operation; for API 500 compatibility, `Min` and `And` explicitly validate older missing-key semantics.

Dependencies and integration points: uses `ReadYourWritesTransaction`, `runRYWTransaction`, `runRYWTransactionNoRetry`, `FDBTransactionOptions::RAW_ACCESS`, transaction atomic APIs, and `getApiVersion()/setApiVersion()` for legacy compatibility. It registers as a tester workload and emits trace events under `AtomicOpCorrectnessApiWorkload`.

Risks and edge cases: lambdas encode expected semantics in the test itself, so changes in API-version rules must update these expectations. The code assumes eight-byte numeric operands for most operations and asserts returned sizes. Empty-value behavior is randomized between clearing and setting an empty value, which improves coverage but makes specific subcase selection seed-dependent.

Test signals: `check()` returns `!testFailed`. Diagnostic trace events include `AtomicOpApiCorrectnessUnexpectedOutput`, `AtomicOpSetOnNonExistingKeyUnexpectedOutput`, `AtomicOpUnsetOnNonExistingKeyUnexpectedOutput`, and `AtomicOpOnEmptyValueUnexpectedOutput`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AtomicOpsApiCorrectness.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/AtomicRestore.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AtomicRestore.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AtomicRestore.cpp

Purpose: defines `AtomicRestore`, a simulation workload that starts a file backup and then repeatedly attempts an atomic restore from that backup while other activity may continue. It is a minimal smoke/stress workload for the `FileBackupAgent::atomicRestore()` path.

Important APIs, types, and functions: `AtomicRestoreWorkload` extends `TestWorkload`. Constructor options include `startAfter`, `restoreAfter`, `backupRanges`, `mutationLogType`, `addPrefix`, and `removePrefix`. `hasPrefix()` detects prefix remapping mode. `_start()` performs the entire workload. The workload registers through `WorkloadFactory<AtomicRestoreWorkload>`.

Control flow: only client 0 runs. `_start()` waits for a randomized fraction of `startAfter`, submits a backup to `file://simfdb/backups/` with default tag, waits for the backup to become active, waits a randomized fraction of `restoreAfter`, and then loops calling `backupAgent.atomicRestore()` with the backup URL, selected ranges, mutation log type, and prefix arguments. Duplicate or unneeded backup errors are tolerated; other errors propagate. After a successful restore, file-backup simulations call `fdbbackupAgents.clear()` to quiesce backup agents.

State and persistence behavior: backup metadata and mutation logs are written by the file backup agent under the normal backup system keyspaces, and backup data is stored in the simulation file container. The workload does not verify restored contents directly; persistent state is managed by `FileBackupAgent`. Prefix remapping is constrained by assertions: both prefixes must be empty in current construction, and `removePrefix` must be empty.

Dependencies and integration points: includes `ManagementAPI`, `BackupAgent`, `BackupContainerFileSystem`, simulator policy state, knobs, tester workload definitions, and `BulkSetup` for range parsing. It exercises backup-agent global state and is sensitive to `FDBBackupAgentType::BackupToFile`.

Risks and edge cases: `check()` always returns true, so failures surface only as thrown actor errors or severe traces from lower layers. The restore loop retries indefinitely on accepted duplicate/unneeded conditions with a fast-spin delay, which can mask a stuck precondition until simulation timeout. Prefix-remap assertions show the workload is not currently a broad prefix-restore validator.

Test signals: successful completion logs `AtomicRestore_Start`, `AtomicRestore_BackupStart`, `AtomicRestore_RestoreStart`, and `AtomicRestore_Done`; unexpected backup or restore exceptions fail the simulation actor.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AtomicRestore.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/AtomicSwitchover.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AtomicSwitchover.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AtomicSwitchover.cpp

Purpose: defines `AtomicSwitchover`, a two-cluster backup-to-DB workload that exercises `DatabaseBackupAgent::atomicSwitchover()` in both directions. It verifies that source data and prefixed backup data match before switching traffic roles.

Important APIs, types, and functions: `AtomicSwitchoverWorkload` extends `TestWorkload`. Constructor options are `switch1delay`, `switch2delay`, and `stopDelay`; it uses default backup ranges from `addDefaultBackupRanges()`, default backup tag, `backupPrefix`, and a simulated extra database. `_setup()` starts a backup from the extra database into the primary. `diffRanges()` compares source ranges with prefixed destination ranges. `_start()` coordinates wait, diff, switchover, reverse wait, reverse diff, reverse switchover, and abort.

Control flow: client 0 submits a backup from `extraDB` into the primary using `DatabaseBackupAgent`. `_start()` waits until that backup is running, delays randomly up to `switch1delay`, diffs all selected ranges, and calls `atomicSwitchover(extraDB, primary, tag, backupPrefix)`. It then treats the primary as the restore/backup source, waits for backup, delays up to `switch2delay`, diffs in the reverse direction, calls `atomicSwitchover(primary, extraDB, tag, "")`, waits again, delays up to `stopDelay`, and aborts the backup on `extraDB`.

State and persistence behavior: backup-to-DB stores copied keys under `backupPrefix` in the destination database and tracks backup configuration, log ranges, and mutation logs in system keyspaces. `diffRanges()` reads batches of 1000 keys from source and destination, strips the backup prefix from destination keys, and emits mismatch traces for key, value, missing-source, and missing-backup cases.

Dependencies and integration points: uses simulator extra databases, `ClusterConnectionMemoryRecord`, `BackupAgent`, `BulkSetup`, and `fdbSimulationPolicyState().drAgents`. It assumes exactly one extra database and clears DR agents when BackupToDB agents are active at completion.

Risks and edge cases: `diffRanges()` logs mismatches but does not throw directly; simulation severity is the enforcement mechanism. It contains a suspicious combined condition for key-and-value mismatch using `&&` before the separate key/value checks, so the first trace is only emitted when both differ. Check always returns true. Timing is intentionally randomized and can race with backup progress.

Test signals: expected traces progress through `AS_Submit*`, `AS_Wait*`, `AS_Ready*`, `AS_Switch*`, `AS_Abort`, and `AS_Done`; severe traces such as `MismatchKey`, `MismatchValue`, `MissingBkpKey`, and `MissingSrcKey` indicate data divergence.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AtomicSwitchover.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/AutomaticIdempotencyWorkload.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AutomaticIdempotencyWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AutomaticIdempotencyWorkload.cpp

Purpose: defines `AutomaticIdempotency`, a simulation workload for automatic and explicit transaction idempotency IDs. It verifies that committed idempotency metadata maps back to exactly the generated transactions and that the background cleaner removes only safe automatic entries.

Important APIs, types, and functions: `ValueType` serializes test transaction metadata (`idempotencyId`, `createdTime`, `automatic`) into user keys. `SharedConfiguration` is stored through a `KeyBackedProperty` under `"\xff\x02/autoIdempotencyWorkload/sharedConfig"` so all clients agree whether automatic idempotency is disabled. `AutomaticIdempotencyWorkload` exposes `_setup()`, `_start()`, `testAll()`, `logIdempotencyIds()`, `testIdempotency()`, `idempotencyKeyValueToTestKeys()`, `getMaxTimestampDelta()`, `getOldestCreatedTime()`, `testCleanerOneIteration()`, `getCreatedTimes()`, and `testCleaner()`.

Control flow: client 0 randomly chooses whether to disable automatic idempotency and writes shared config. Other clients wait until it appears. `_start()` creates `numTransactions` transactions per client, chooses a 16-byte or variable-length idempotency ID, randomly marks it automatic according to `automaticPercentage`, optionally sets `AUTO_THROTTLE_IDEMPOTENCY_IDS`, writes a `ValueType` under `keyPrefix`, and commits with either automatic or explicit idempotency ID. `check()` runs only on client 0, logging idempotency metadata, verifying all expected IDs are represented, then repeatedly invoking the cleaner while raising the minimum age threshold until automatic entries disappear safely.

State and persistence behavior: user-visible test rows live under `keyPrefix` (default `/autoIdempotency/`). FoundationDB idempotency metadata lives under `idempotencyIdKeys` and encodes commit versions, timestamps, and affected test keys. The shared configuration is a system-key backed property. Cleaner validation reads idempotency metadata, decodes linked user keys, and compares stored `createdTime` values against metadata timestamps to tolerate timestamp skew.

Dependencies and integration points: depends on `KeyBackedTypes`, idempotency transaction options, `RunRYWTransaction`, `ReadYourWrites`, Flow coroutine utilities, `recurringAsync`, and `cleanIdempotencyIds()`. It exercises commit proxy idempotency metadata creation and the cleaner API rather than a standalone unit-test path.

Risks and edge cases: the `ValueType` format is explicitly only safe within one test run and not an upgrade-stable persisted encoding. Cleaner tests rely on timestamp slop (`1.5`) and repeated success cycles, so timing-sensitive failures may be intermittent. When automatic idempotency is disabled, the cleaner expectations differ and the workload allows all entries to be manual. Large client counts or transaction counts can hit `TOO_MANY` range limits because the checks assert full-range reads are not truncated.

Test signals: severe traces include `IdempotencyCommitMissingVersion`, `IdempotencyIdsWrongCount`, `AutomaticIdempotencyKeyMissing`, and `AutomaticIdempotencyCleanedTooMuch`. Success requires `testIdempotency()` to find `clientCount * numTransactions` unique IDs and `testCleaner()` to reach stable cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AutomaticIdempotencyWorkload.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/BackgroundSelectors.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackgroundSelectors.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BackgroundSelectors.cpp

Purpose: defines `BackgroundSelectors`, a background consistency workload for key selectors. It continuously compares `getKey()` selector results with bounded `getRange()` results to catch selector/range disagreement under concurrent database activity.

Important APIs, types, and functions: `randomizedSelector()` sometimes rewrites an `orEqual` selector into an equivalent `keyAfter(key)` form. `BackgroundSelectorWorkload` extends `TestWorkload`; constructor options include `testDuration`, `actorsPerClient`, `maxDiff`, `minDiff` (used for `minDrift`), `transactionsPerSecond`, and fixed `resultLimit=100`. `backgroundSelectorWorker()` owns the selector/range loop. Metrics report approximate transactions and actors.

Control flow: `start()` launches `actorsPerClient` workers and waits for `testDuration`. Each worker repeatedly chooses forward or backward direction, obtains initial boundary keys with `getKey()`, then periodically selects drift offsets and a range length (`diff`). It fetches the range between randomized selectors and separately fetches start/end selector results. If the returned range is shorter than the limit and not truncated by the beginning sentinel, it verifies that first and last keys match the independent selector results.

State and persistence behavior: no data is written by this workload. It reads `allKeys`, user/system boundaries, and live key contents through ordinary transactions. Worker state is entirely in memory: start/end keys, drifts, diff, direction, and restart flags.

Dependencies and integration points: uses `NativeAPI.actor.h`, `TesterInterface`, Flow coroutine transactions, `KeySelectorRef`, `keyAfter`, `allKeys`, and tester workload scheduling. It is intended to run alongside data-mutating workloads, increasing coverage of selector semantics under changing keyspaces.

Risks and edge cases: both `minDrift` and `maxDrift` are read from the `"minDiff"` option, which appears accidental and means a configured max drift option would be ignored. Empty ranges or limit-truncated ranges cause restarts or reduce checking strength. Because data can change between retries, correctness depends on each validation transaction seeing a consistent snapshot.

Test signals: `check()` scans worker futures for errors. Main correctness failures emit `BackgroundSelectorError` with direction, drift, diff, range size, expected selector result, and actual boundary key.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackgroundSelectors.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/BackupAndRestoreValidation.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupAndRestoreValidation.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BackupAndRestoreValidation.cpp

Purpose: defines `BackupAndRestoreValidation`, a compact file-backup workload used to validate that a restore completed and to signal other validation logic through a system-key completion marker.

Important APIs, types, and functions: `restoreValidationCompletionKey` is `"\xff\x02/restoreValidationComplete"`. `BackupAndRestoreValidationWorkload` extends `TestWorkload`; options are `backupAfter`, `restoreAfter`, `backupTag`, and `addPrefix`. `doBackup()` submits and waits for a file backup. `doRestore()` submits a restore, waits for completion, delays for stabilization, writes the completion marker, and unlocks the database. `_start()` coordinates retries.

Control flow: client 0 waits `backupAfter`, runs `doBackup()` into `file://simfdb/backups/`, reads the backup tag metadata to find the container URL, waits until `restoreAfter`, and invokes `doRestore()`. The restore uses `normalKeys` as the restore range, optional `addPrefix`, empty `removePrefix`, and waits for completion. Retryable memory-limit, lock, transaction-too-old, and future-version errors are retried with bounded backoff; other errors are logged as severe and rethrown.

State and persistence behavior: backup metadata is stored through `FileBackupAgent` system keyspaces and backup contents in the file container. The workload writes `restoreValidationCompletionKey` with value `"done"` using `ACCESS_SYSTEM_KEYS` and later unlocks the database with the restore tag. It does not directly compare restored rows.

Dependencies and integration points: includes `ManagementAPI`, `ReadYourWrites`, `BackupAgent`, `BackupContainer`, `SystemData`, `QuietDatabase`, and tester workload definitions. It relies on `makeBackupTag`, `BackupConfig(logUid).backupContainer()`, and standard file-backup restore APIs.

Risks and edge cases: `check()` always returns true, so validation depends on actor completion and the marker being consumed by other workloads or test logic. `restoreAfter - backupAfter` is assumed non-negative in `_start()`. The fixed five-second stabilization delay is a timing heuristic rather than a direct durability proof.

Test signals: progress traces include `BARV_SubmitBackup`, `BARV_BackupComplete`, `BARV_StartRestore`, `BARV_RestoreComplete`, `BARV_RestoreCompletionMarkerSet`, and `BARV_Complete`; retryable failures emit `BARV_RetryableError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupAndRestoreValidation.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/BackupCorrectness.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BackupCorrectness.cpp

Purpose: defines `BackupAndRestoreCorrectness`, the main file-backup correctness workload. It covers backup submission, optional differential backup, abort/restart, range filtering, restore to one or multiple tags, restore abort/retry, system-key restore handling, encryption, dirty-restore rejection, and backup metadata cleanup.

Important APIs, types, and functions: `BackupAndRestoreCorrectnessWorkload` extends `TestWorkload`. Options include `backupAfter`, `minBackupAfter`, `restoreAfter`, `performRestore`, `backupTag`, `backupRangesCount`, `backupRangeLengthMax`, `abortAndRestartAfter`, `differentialBackup`, `stopDifferentialAfter`, `simBackupAgents`, `allowPauses`, `shareLogRange`, `defaultBackup`, `restorePrefixesToInclude`, and `encrypted`. Helpers include `changePaused()`, `statusLoop()`, `doBackup()`, `attemptDirtyRestore()`, `clearAndRestoreSystemKeys()`, `_start()`, and `_check()`.

Control flow: constructor builds backup ranges either from default backup ranges, random sorted endpoints, special shared-log ranges, or prefix-filtered ranges; it may also choose skipped restore ranges. `_setup()` may add system backup ranges under buggify. `_start()` optionally creates an encryption key file, delays to `backupAfter`, starts a file backup, possibly aborts/restarts it, optionally starts another concurrent backup, waits until `restoreAfter`, describes the backup container, checks that dirty restore is rejected, clears the target ranges, chooses a target version, restores system-key ranges first, then restores remaining ranges either one range per restore tag or multiple ranges in one tag. Under buggify it aborts restore jobs and restarts only those that actually aborted. Finally it waits for all restores, aborts any extra backup, and checks for leftover task/config/log keys.

State and persistence behavior: backup state lives in file-backup system keyspaces, task bucket keys, backup latest-version keys, mutation log keys, and `file://simfdb/backups/`. Restore clears selected ranges and writes restored data to the original keyspace. Skipped restore ranges are expected to remain absent after check. Cleanup inspection derives keys from `logUid`, `destUidValue`, `backupLogKeys`, and `backupLatestVersionsPrefix`.

Dependencies and integration points: integrates with `FileBackupAgent`, `BackupContainerFileSystem`, `IBackupContainer`, `BackupDescription`, `TaskBucket`, `DatabaseConfiguration`, encryption test utilities, simulator backup-agent state, and `BulkSetup` range helpers. It disables `RandomRangeLock` because the workload also uses database/range locks.

Risks and edge cases: `check()` only verifies skipped ranges; most correctness is enforced by actor assertions and severe trace diagnostics. Range construction and target-version choice are randomized, so coverage depends on seeds. Cleanup waits for task count to drain and can extend test time. Dirty restore expects `restore_destination_not_empty`; changes to restore preconditions can break the test. When `shareLogRange` is true, leftover log-key expectations are relaxed if latest-version metadata indicates shared logs.

Test signals: severe traces include `BARW_RestoreAllowedOverwrittingDatabase`, `BARW_UnexpectedRangePresent`, `BARW_MissingBackupContainer`, `BARW_NotRestorable`, `BackupCorrectnessLeftOverMutationKeys`, `BackupCorrectnessLeftOverVersionKey`, `BackupCorrectnessLeftOverLogKeys`, and top-level `BackupAndRestoreCorrectness`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupCorrectness.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/BackupCorrectnessPartitioned.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupCorrectnessPartitioned.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BackupCorrectnessPartitioned.cpp

Purpose: defines `BackupAndRestorePartitionedCorrectness`, a file-backup variant that restores selected ranges as partitioned work. It is close to `BackupCorrectness.cpp` but emphasizes splitting user and system ranges, restoring multiple normal ranges, and verifying that skipped ranges remain absent.

Important APIs, types, and functions: `BackupAndRestorePartitionedCorrectnessWorkload` extends `TestWorkload`. Constructor options mirror the main file-backup workload: timing knobs, backup tag, backup-range generation, differential mode, pause allowance, shared log ranges, default backup, restore prefix filtering, and optional encryption. Helpers include `changePaused()`, `statusLoop()`, `doBackup()`, `clearAndRestoreSystemKeys()`, `_start()`, and `_check()`.

Control flow: client 0 optionally adds system backup ranges, starts and possibly pauses backup-agent tasks, creates an encryption key if configured, delays until backup start, runs `doBackup()`, waits for backup completion or allowed database-lock failure, reads backup metadata and container, waits for restore time, clears backup ranges, selects a target restorable version, separates system ranges from normal ranges, restores system ranges first, then launches one restore per selected normal range using distinct restore tags. It waits for all restore futures, then checks backup task/config/log/latest-version cleanup.

State and persistence behavior: backup metadata and mutation logs are in the same file-backup system keyspaces as `BackupCorrectness.cpp`, with destination UID paths derived from `BackupConfig(logUid)`. Restore state is spread across tags named from the backup tag plus range index. Skipped ranges are kept in `skippedRestoreRanges` and verified by `_check()`.

Dependencies and integration points: depends on `FileBackupAgent`, `TaskBucket`, `IBackupContainer`, `BackupContainerFileSystem`, encryption test support, `DatabaseConfiguration`, simulator backup-agent policy state, and system backup ranges. It disables `RandomRangeLock`.

Risks and edge cases: because each normal range may become an independent restore, failures can be partial and must be diagnosed per restore tag. System-key ranges require special clear-and-restore handling before normal ranges. Like the main workload, cleanup polling can be slow, and `check()` does not compare restored data byte-for-byte. Prefix filtering or random skipped ranges can produce empty restore ranges, so constructor assertions and fallback behavior matter.

Test signals: failures are visible through severe traces such as `BARW_UnexpectedRangePresent`, `BARW_NotRestorable`, `BackupCorrectnessLeftOverMutationKeys`, `BackupCorrectnessLeftOverVersionKey`, `BackupCorrectnessLeftOverLogKeys`, and top-level `BackupAndRestorePartitionedCorrectness`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupCorrectnessPartitioned.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/BackupS3BlobCorrectness.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupS3BlobCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BackupS3BlobCorrectness.cpp

Purpose: defines `BackupS3BlobCorrectness`, a file-backup correctness workload specialized for blobstore/S3-style backup containers. It extends backup/restore coverage with MockS3 registration, chaos injection, BulkDump/BulkLoad modes, restorable-state polling, and optional audit-based validation.

Important APIs, types, and functions: `BackupS3BlobCorrectnessWorkload` extends `TestWorkload`. It has standard backup options plus S3-specific `backupURL`, `skipDirtyRestore`, `initSnapshotInterval`, `snapshotInterval`, `snapshotMode`, `useRangeFileRestore`, `performValidation`, `enableChaos`, `errorRate`, `throttleRate`, `delayRate`, `corruptionRate`, and `maxDelay`. Helpers include `_setup()` for MockS3 registration, `changePaused()`, `statusLoop()`, `verifyBulkDumpObservability()`, `waitForRestorable()`, `doBackup()`, and `_start()`. External counters `g_bulkDumpTaskCompleteCount` and `g_bulkLoadRestoreTaskCompleteCount` assert bulk paths ran.

Control flow: `_setup()` registers either a normal MockS3 server or chaos server for `blobstore://` URLs in simulation. `_start()` aborts stale metadata for the tag, starts the backup, optionally aborts and restarts, then for restore waits until backup completion and an additional metadata delay. It obtains the backup container from `BackupConfig`, polls until restorable, locks the database, optionally performs a traditional validation restore into `\xff\x02/rlog/`, optionally clears normal ranges, restores selected ranges using either range-file restore or BulkLoad, asserts BulkLoad usage when configured, optionally runs `auditStorage(..., AuditType::ValidateRestore, ...)`, monitors audit completion, and cleans validation data. It also asserts BulkDump usage when `snapshotMode` requests it.

State and persistence behavior: backup contents live in the configured file/blob container, while metadata lives under file-backup system keyspaces. MockS3 persistence is intentionally not cleared after registration because container metadata may need it. Validation temporarily writes restored data under the system prefix `\xff\x02/rlog/` and then clears it. Database locks use a generated `lockUID` shared across restore calls.

Dependencies and integration points: integrates with `MockS3Server`, `MockS3ServerChaos`, `Audit`, `AuditUtils`, `BulkDump`/`BulkLoad` observability, file backup agents, encryption test files, simulator policy state, and backup containers. It disables `RandomRangeLock`.

Risks and edge cases: comments note restart cleanup must keep FDB metadata and MockS3 contents in sync. Chaos settings can surface transient object-store failures that require careful distinction from correctness failures. Audit scheduling retries only timeout and audit-storage-failed errors. `skipDirtyRestore` changes whether normal keys are cleared before restore. The workload relies on global bulk task counters, so unrelated bulk work in the same process could affect assertions.

Test signals: severe traces include `BS3BCW_BackupNotRestorableAfterWait`, `BS3BCW_ValidationStep1_Failed`, `BS3BCW_ValidationAuditFailed`, and `BS3BCW_ValidationAuditTimeout`. Successful bulk modes emit `BS3BCW_AssertBulkDumpUsed`, `BS3BCW_AssertBulkLoadUsed`, and `BS3BCW_ValidationAuditComplete`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupS3BlobCorrectness.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBAbort.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBAbort.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBAbort.cpp

Purpose: defines `BackupToDBAbort`, a small backup-to-DB workload that starts a DR backup, waits, locks the primary database, aborts the backup, unlocks the backup state, and later unlocks the database. It focuses on abort/lock cleanup behavior.

Important APIs, types, and functions: `BackupToDBAbort` extends `TestWorkload`; the main option is `abortDelay`. `_setup()` submits a default-tag backup from the simulated extra database to the primary with default backup ranges and a fixed backup prefix. `_start()` performs the timed abort sequence. `check()` unlocks the database and returns true. It registers through `WorkloadFactory<BackupToDBAbort>`.

Control flow: only client 0 runs. Setup creates `extraDB`, instantiates `DatabaseBackupAgent`, submits backup with `StopWhenDone::False`, and tolerates duplicate backup errors. Start waits `abortDelay`, waits for the backup to be active, generates a lock UID, locks the primary database, aborts the backup on `extraDB`, unlocks the backup tag, and completes. Check releases the primary database lock.

State and persistence behavior: DR backup metadata and copied data are stored by `DatabaseBackupAgent` in the participating databases. The workload stores only an in-memory `UID lockid` but persists the database lock until `check()`. It does not compare copied data or inspect leftover metadata.

Dependencies and integration points: depends on `BackupAgent`, `ManagementAPI`, `NativeAPI.actor.h`, tester workload definitions, simulator extra databases, `lockDatabase`, `unlockDatabase`, and `unlockBackup`. It assumes one configured extra database.

Risks and edge cases: if `_start()` fails after locking but before `check()`, the database can remain locked until simulation teardown or another cleanup path. `check()` always returns true after unlocking and does not validate backup-agent state. The workload is intentionally narrow and should be paired with broader correctness tests.

Test signals: actor completion without unexpected exceptions is the primary signal; duplicate backup is tolerated, while other backup submission errors fail setup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBAbort.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBCorrectness.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBCorrectness.cpp

Purpose: defines `BackupToDBCorrectness`, the main correctness workload for backing up one simulated cluster into another database and optionally restoring it back. It tests backup-to-DB range copying, prefix handling, abort/restart, differential stop, system-key split restore, destination clearing, and cleanup of DR metadata.

Important APIs, types, and functions: `BackupToDBCorrectnessWorkload` extends `TestWorkload`. Options include backup and restore timing, `performRestore`, `backupTag`, `restoreTag`, `backupPrefix`, backup range count/length, `abortAndRestartAfter`, `differentialBackup`, `stopDifferentialAfter`, `simDrAgents`, `shareLogRange`, and `defaultBackup`. Helpers include `readRanges()`, `diffRanges()`, `doBackup()`, `checkData()`, and `_start()`.

Control flow: constructor derives `backupPrefix` and `extraPrefix` so backed-up data does not collide with normal source ranges, creates random/default/shared ranges, and opens the simulated extra database. `_setup()` may add system backup ranges. `_start()` starts a backup from `extraDB`, may abort and restart it, possibly starts an extra concurrent backup into `extraPrefix`, waits for restore time, and if requested submits restore-like backup jobs from primary back into `extraDB`: system ranges first, then prefixed user ranges under `restoreTag`. It verifies restored ranges stop changing by reading them, delaying, and reading again. It waits for any extra backup, aborts it with `WaitForDestUID`, then runs `checkData()` on source and restore tags.

State and persistence behavior: DR metadata is keyed by log UID and destination UID under `logRangesRange`, `backupLogKeys`, and `backupLatestVersionsPrefix`. Copied user data is written with `backupPrefix` in the destination. `DatabaseBackupAgent::PreBackupAction::CLEAR` is used to clear the destination prefix atomically with backup setup, avoiding retry problems after `commit_unknown_result`.

Dependencies and integration points: integrates with `DatabaseBackupAgent`, `ClusterConnectionMemoryRecord`, simulator extra databases, `BulkSetup`, `TaskBucket`, `DatabaseConfiguration`, `FDBOptions`, `lockDatabase` semantics, and global `fdbSimulationPolicyState().drAgents`. It disables `RandomRangeLock`.

Risks and edge cases: `check()` returns true, so data comparison is mostly via `diffRanges()` severe traces and post-restore stability assertions. The code comments document a historical `submitBackup` retry issue, making the pre-backup action important. Extra backup abort can race with destination UID creation, hence `WaitForDestUID`. Shared-log mode relaxes some leftover-log checks. Prefix splitting and system-key handling are subtle and can produce false failures if ranges overlap unexpected system backup ranges.

Test signals: severe traces include `MismatchKey`, `MismatchValue`, `MissingBkpKey`, `MissingSrcKey`, `BackupCorrectnessLeftoverMutationKeys`, `BackupCorrectnessLeftoverVersionKey`, `BackupCorrectnessLeftoverLogKeys`, and top-level `BackupAndRestoreCorrectness`. Successful runs decrement `drAgentRequests` and may disable BackupToDB agents when no requests remain.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBCorrectness.cpp -->

## sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBUpgrade.cpp
<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBUpgrade.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBUpgrade.cpp

Purpose: defines `BackupToDBUpgrade`, a backup-to-DB workload for DR version upgrade and switchover-style restore paths. It starts an older/differential backup, waits for upgrade to the latest DR version, locks/apply-checks the backup, aborts it, then restores data back through another backup-to-DB job.

Important APIs, types, and functions: `BackupToDBUpgradeWorkload` extends `TestWorkload`. Options include `backupAfter`, `backupPrefix`, `backupRangeLengthMax`, `stopDifferentialAfter`, `backupTag`, `restoreTag`, and `backupRangesCount`. Helpers include `doBackup()`, `checkData()`, `_setup()`, `diffRanges()`, and `_start()`.

Control flow: constructor creates non-overlapping `backupPrefix`/`extraPrefix`, random or whole ranges, and an extra database. `_setup()` optionally adds system backup ranges, waits `backupAfter`, and starts the backup on `extraDB`. `_start()` waits for both `stopDifferentialAfter` and `waitUpgradeToLatestDrVersion()`, reads the log UID and backed-up range list from backup config, locks the extra database for the log UID, waits until `appliedVersion >= commitVersion`, diffs copied ranges against primary data, aborts and unlocks the original backup, prepares restore ranges by prefixing the previous backup ranges, submits a restore backup into the primary, waits/unlocks it, and runs `checkData()` for both the original backup and restore tag.

State and persistence behavior: the workload inspects and manipulates backup-to-DB config keys directly through `DatabaseBackupAgent::config`, including serialized `VectorRef<KeyRangeRef>` backup ranges, log UID, destination UID, applied-version keys, log ranges, latest-version keys, and mutation log keys. It locks databases during apply/restore transitions and clears restore destination ranges before submitting the restore backup.

Dependencies and integration points: uses `FDBOptions.g.h`, `BackupAgent`, `ClusterConnectionMemoryRecord`, `ManagementAPI`, `ApiVersion`, simulator extra databases, `BulkSetup`, `TaskBucket`, and backup config primitives. It assumes exactly one extra database and disables `RandomRangeLock`.

Risks and edge cases: it performs lower-level config reads and lock operations than most workloads, so schema or encoding changes in backup config can break it. The applied-version watch loop must handle races where the watched value is already high enough. `diffRanges()` logs rather than throws on data mismatch. Restore setup prints ranges to stdout and clears prefixed ranges under retry. `checkData()` waits for task drain and can be slow.

Test signals: expected traces include `DRU_DoBackup`, `DRU_WaitDifferentialEnd`, `DRU_Locked`, `DRU_Applied`, `DRU_DiffRanges`, `DRU_AbortBackup`, `DRU_PrepareRestore`, `DRU_RestoreDb`, and `DRU_Complete`. Severe traces include `BackupCorrectnessLeftoverMutationKeys`, `BackupCorrectnessLeftoverVersionKey`, `BackupCorrectnessLeftoverLogKeys`, and top-level `BackupAndRestoreCorrectnessError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBUpgrade.cpp -->

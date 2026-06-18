# Research Group subset-b-008493

This grouped report covers FoundationDB simulation workload sources under `sources/storage-engines/foundationdb/fdbserver/workloads`. Each section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReportConflictingKeys.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ReportConflictingKeys.cpp

## Purpose
`ReportConflictingKeysWorkload` validates the `REPORT_CONFLICTING_KEYS` transaction option and the transaction special key range under `conflictingKeysRange`. It creates two transactions at the same read version, commits one with random write conflict ranges, and verifies that a conflicting second transaction reports key ranges consistent with its read conflict ranges and the first transaction's write conflict ranges.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `ReportConflictingKeys`. Important members include `keyForIndex`, `addRandomReadConflictRange`, `addRandomWriteConflictRange`, `emptyConflictingKeysTest`, and `conflictingClient`. It uses `ReadYourWritesTransaction`, `FDBTransactionOptions::REPORT_CONFLICTING_KEYS`, optional `READ_YOUR_WRITES_DISABLE`, `conflictingKeysRange`, `conflictingKeysTrue`, `conflictingKeysFalse`, and `validateSpecialSubrangeRead`.

## Control Flow
`start` clones the database and runs `conflictingClient` until `testDuration` expires. Each loop enables conflict reporting, verifies a fresh transaction has no conflicting keys, shares a read version between two transactions, commits `tr1`, then attempts to commit `tr2`. On `not_committed`, it reads `\xff\xff/transaction/conflicting_keys/`, checks local special-key read validation, and walks start/end marker pairs. If `tr2` commits, it independently verifies that no `tr2` read range intersected any `tr1` write range. Both transactions are reset after retries or success.

## State And Persistence Behavior
The workload writes no ordinary key values; it only manipulates transaction conflict ranges and observes resolver-produced conflict metadata exposed through special keys. Counters track invalid reports, commits, conflicts, and total completed transaction attempts. Conflict range vectors are local state cleared every loop.

## Dependencies And Integration Points
It depends on NativeAPI, `ReadYourWrites`, `SystemData`, tester workload registration, and `BulkSetup` key helpers. It disables `RandomRangeLock` because that workload intentionally causes range-lock conflicts that would invalidate this workload's conflict attribution assumptions.

## Risks And Edge Cases
The test assumes resolver conflict reporting returns merged ranges that contain at least one original read conflict range and intersect at least one write conflict range. It is sensitive to RYW conflict-range merging differences, special-key range prefix encoding, and the `TOO_MANY` limit. The source comments note it requires buggify and connection failure behavior to be disabled for reliable reporting.

## Test Signals
`check` passes only when `InvalidReports` is zero. Failure signals include `TestFailure` trace events for impossible missing conflicts, reported ranges that do not contain expected read ranges, reported ranges that do not intersect write ranges, and malformed special-key start/end marker pairs. Metrics expose transactions/sec, commits/sec, and conflicts/sec.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReportConflictingKeys.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ResolverBug.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ResolverBug.cpp

## Purpose
`ResolverBugWorkload` is a negative-test harness for simulated resolver bugs. It enables a `ResolverBug` injector with configurable probabilities, repeatedly runs the existing `Cycle` workload while toggling the injector, and treats any `TestFailure` error trace as expected evidence that the injected resolver bug was detected.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `ResolverBug`. Key members are `ResolverBug resolverBug`, `cycleOptions`, `createCycle`, `driveWorkload`, `_start`, `waitForPhase`, `waitForPhaseDone`, and `onBug`. It uses `SimBugInjector`, `ResolverBugID`, `ProcessEvents::Event`, and `BaseTraceEvent` severity inspection.

## Control Flow
The constructor strips options with a `cycle_` prefix into `cycleOptions`, installs the bug injector on client 0, and sizes `bug->cycleState` to the client count. Client 0 runs `driveWorkload`, which cycles phases: setup with injector disabled, start with injector enabled, and check with injector disabled. Every client runs `_start`, which creates a fresh `Cycle` workload for each phase and records its client phase in shared bug state. `start` races phase execution with `onBug`, which logs `NegativeTestSuccess` once a severe `TestFailure` trace is observed.

## State And Persistence Behavior
The durable database state is whatever the nested `Cycle` workload writes. Resolver bug configuration and phase state live in the process-local simulation bug injector. `bugFound` is a shared in-memory flag set by trace observation rather than by reading database state.

## Dependencies And Integration Points
It depends on `flow/ProcessEvents`, `fdbserver/resolver/ResolverBug.h`, `ServerDBInfo`, and the workload factory interface. It can disable all failure injection workloads by default so the observed failure is attributable to resolver bug injection rather than unrelated chaos.

## Risks And Edge Cases
The workload is intentionally successful only when a failure is detected. If no `TestFailure` is emitted, it runs indefinitely through `waitForAll`. It relies on trace-event process hooks and global `g_traceProcessEvents`, so unrelated code changing trace names, severities, or process event delivery can break the negative-test signal.

## Test Signals
The positive signal is `NegativeTestSuccess`. Severe `TraceEvent::TestFailure` events set `bug->bugFound`. `check` always returns true because success is encoded in the early completion path, not final database validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ResolverBug.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Restore.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/Restore.cpp

## Purpose
`RestoreWorkload` validates backup-agent restore behavior from the most recent backup container for a selected tag. It optionally performs a restore, then checks backup-agent task queues and backup metadata/log subspaces for leftovers.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `Restore`. Important state includes `backupTag`, `backupRanges`, `restoreRanges`, `LockDB locked`, `allowPauses`, `shareLogRange`, static `backupAgentRequests`, and a per-run `randomID`. Key actors are `changePaused`, `resumeAgent`, `statusLoop`, and `_start`. It uses `FileBackupAgent`, `BackupConfig`, `KeyBackedTag`, `BackupDescription`, `IBackupContainer`, `runRYWTransaction`, `getSystemBackupRanges`, `TaskBucket::debugPrintRange`, and simulation backup-agent policy state.

## Control Flow
Only client 0 runs. `_start` optionally toggles backup-agent pause state, starts a status loop, increments the static backup-agent request counter, resolves the backup tag to a log UID and container, and, when `performRestore` and a container exist, picks a target version from the container's restorable range. It clears backed-up ranges, filters restore ranges to exclude system backup ranges except normal-key intersections, and calls `backupAgent.restore` with a derived restore tag. After restore or no-restore operation, it waits for task count to drain and checks backup agent configuration keys, latest-version keys, and backup log value keys.

## State And Persistence Behavior
The workload clears `normalKeys` before restore and may restore only filtered normal-key ranges. It reads and validates system backup metadata under `logRangesRange`, `backupLatestVersionsPrefix`, and `backupLogKeys`. It can lock the database during restore, unlock afterward through restore parameters, and mutate simulation backup-agent policy when the final simulated request completes.

## Dependencies And Integration Points
It integrates deeply with FoundationDB's file backup agent, backup containers, task bucket metadata, system keyspace backup ranges, simulation policy state, and the tester workload runner. The `allowPauses` buggify path stresses backup-agent pause/resume while restore or status operations run.

## Risks And Edge Cases
The restore target version is randomized across min, max, an interior version, or latest restore. The leftover-key checks are sensitive to shared log ranges and to asynchronous task cleanup. Because the status loop and pause loop are not explicitly cancelled in `_start`, normal actor lifetime cancellation must clean them up. The static request counter must remain balanced across errors; exceptions rethrow after logging.

## Test Signals
Trace signals include `RW_Restore`, `RW_RestoreRanges`, `RW_CheckLeftoverTasks`, `BackupCorrectnessLeftOverMutationKeys`, `BackupCorrectnessLeftOverVersionKey`, `BackupCorrectnessLeftOverLogKeys`, and `RW_Complete`. The workload's `check` returns true, so errors are surfaced through assertions, thrown errors, and severe trace events during `_start`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Restore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RestoreBackup.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/RestoreBackup.cpp

## Purpose
`RestoreBackupWorkload` waits for an existing tagged backup to be usable, clears database and backup-system ranges, then restores the backup into the same cluster. It is a compact end-to-end restore consumer of backup-agent state.

## Important APIs, Types, And Functions
It derives from `TestWorkload` and registers as `RestoreBackup`. Important members are `FileBackupAgent backupAgent`, `Reference<IBackupContainer> backupContainer`, `backupDir`, `tag`, `delayFor`, `stopWhenDone`, and optional `encryptionKeyFileName`. Key actors are `waitOnBackup`, `clearDatabase`, and `_start`.

## Control Flow
Client 0 delays by `delayFor`, records a read version as a lower bound, waits for the backup tag, and handles either completed backups or running differential backups. For running differential backups with `stopWhenDone=false`, it polls the container description until contiguous log end reaches the captured read version, then discontinues the backup. It clears `normalKeys` and system backup ranges with system-key access and invokes `backupAgent.restore` with `WaitForComplete::True`, `LockDB::True`, and encryption parameters if a test encryption file exists.

## State And Persistence Behavior
The workload destroys current normal-key data and clears all system backup ranges before restore. It reads backup container metadata to determine log completeness. It may discontinue a running differential backup and may lock the database during restore.

## Dependencies And Integration Points
It depends on ManagementAPI, backup agent/container APIs, filesystem backup containers, simulator support, and test encryption utility helpers. It uses `getSystemBackupRanges()` to avoid leaving backup metadata in the restored cluster before applying backup contents.

## Risks And Edge Cases
The workload assumes an external backup has already been submitted. If the backup state is neither completed nor running differential, it emits `BadBackupState` and asserts. The captured read version gate avoids restoring a differential backup before it includes the desired point, but polling every five seconds can extend runtime under slow simulation.

## Test Signals
`BadBackupState`, `BackupVersionGate`, `DiscontinuingBackup`, and restore exceptions are the main signals. `check` always returns true; failures propagate through assertions or errors in `start`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RestoreBackup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RestoreMultiRanges.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/RestoreMultiRanges.cpp

## Purpose
`RestoreMultiRangesWorkload` verifies that restoring a subset of backed-up ranges restores only the selected keys. It backs up keys in `[a,z)`, clears the database, restores two disjoint subranges, and checks that key `b` was skipped.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `RestoreMultiRanges`. Important functions are `clearDatabase`, `prepareDatabase`, `logTestData`, `verifyDatabase`, and `_start`. It uses `FileBackupAgent`, `IBackupContainer`, `BackupContainerFileSystem::createTestEncryptionKeyFile`, `submitBackup`, `waitBackup`, and `restore`.

## Control Flow
Client 0 clears normal keys, writes five known keys (`a`, `aaaa`, `b`, `bb`, `bbb`), optionally creates an encryption key file, and submits a stop-when-done backup over `[a,z)`. After waiting for completion, it clears the database and restores `[a,aaaaa)` plus `[bb,bbbbb)`. `check` runs `verifyDatabase`, expecting exactly four keys: `a`, `aaaa`, `bb`, and `bbb`.

## State And Persistence Behavior
The workload intentionally creates, removes, and restores normal-key data. It writes backup files under `file://simfdb/backups/` and may create a simulation encryption key file. Restore runs with database lock/unlock enabled and without applying mutation logs only.

## Dependencies And Integration Points
It integrates with the file backup agent, file-system backup container, encryption test utilities, and the tester workload lifecycle. It exercises the restore overload that accepts an explicit `VectorRef<KeyRangeRef>` range list.

## Risks And Edge Cases
It tolerates `backup_unneeded` and `backup_duplicate` on submission. The verification only checks key order and membership, not values, although the prepared values match keys. A range boundary bug would show up because `b` sits outside both restore ranges while nearby `bb` and `bbb` should restore.

## Test Signals
Success traces include `RestoreMultiRanges_VerifyPassed` and `RestoreMultiRanges_Success`. Failure emits `TestFailureInfo` and `CurrentDataEntry` traces with actual range contents. `check` returns the verifier result.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RestoreMultiRanges.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RestoreValidation.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/RestoreValidation.cpp

## Purpose
`RestoreValidationWorkload` schedules and monitors a `ValidateRestore` audit after another workload finishes a prefixed backup/restore validation flow. It waits for a completion marker, starts audit storage validation over `normalKeys`, and fails if the audit does not reach the expected phase.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `RestoreValidation`. Important options are `validateAfter`, `expectedPhase`, `expectSuccess`, `checkInterval`, and `maxWaitTime`. `_start` uses `auditStorage`, `getAuditStates`, `AuditStorageState`, `AuditType::ValidateRestore`, `AuditPhase`, `IClusterConnectionRecord`, system-key reads, `LOCK_AWARE`, and several audit-specific errors.

## Control Flow
Only client 0 runs. It delays by `validateAfter`, then polls the system key `\xff\x02/restoreValidationComplete` until present, retrying known transient errors. It schedules a validate-restore audit with a 60-second scheduling timeout, then polls audit states every `checkInterval`, filtering by the returned audit ID. It reports progress every ten seconds, enforces `maxWaitTime`, and retries the whole audit up to five times on `audit_storage_failed`.

## State And Persistence Behavior
The workload does not write user data. It reads a system completion marker and creates audit storage metadata through the management API. Audit state is durable cluster metadata managed by the audit subsystem, not by this workload directly.

## Dependencies And Integration Points
It is designed to coordinate with `BackupAndRestoreValidation`, which creates the restored prefix and writes the marker. It depends on `fdbclient/Audit.h`, `AuditUtils`, `ManagementAPI`, and the cluster connection record. It is sensitive to buggify-induced recovery delays and includes retry/backoff paths for cluster instability.

## Risks And Edge Cases
There is no maximum wait for the completion marker beyond the surrounding simulation timeout, by design. Audit states can temporarily disappear or time out during recovery; the workload logs warnings but continues until overall timeout. The `expectedPhase` option is stored but the success path primarily checks `AuditPhase::Complete` when `expectSuccess` is true.

## Test Signals
Success emits `RestoreValidationSuccess` with the audit ID. Failures include `RestoreValidationTimeout`, `RestoreValidationUnexpectedPhase`, `RestoreValidationUnexpectedError`, `RestoreValidationUnexpectedSuccess`, and `RestoreValidationError`. `check` itself returns true; actor errors are the real signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RestoreValidation.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Rollback.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/Rollback.cpp

## Purpose
`RollbackWorkload` is a failure injection workload that tries to force transaction log rollback scenarios by partitioning a commit proxy from most tLogs, then either rebooting or clogging the proxy and the remaining tLog interface.

## Important APIs, Types, And Functions
It derives from `FailureInjectionWorkload` and registers both a workload factory and failure-injector factory under `Rollback`. Important options include `meanDelay`, `clogDuration`, `testDuration`, `enableFailures`, and `multiple`. Core actors are `simulateFailure` and `rollbackFailureWorker`.

## Control Flow
Only client 0 is enabled. In simulation, `start` runs `rollbackFailureWorker` until `testDuration`. In multiple mode, failures are scheduled by Poisson delay; otherwise a single failure is delayed within the test window. `simulateFailure` reads current `ServerDBInfo`, chooses a random commit proxy and tLog, clogs proxy links to all other tLogs, waits one third of the clog duration, refreshes system info, and then either reboots the proxy plus clogs the remaining tLog or clogs both interfaces.

## State And Persistence Behavior
The workload does not directly write keys. Its state changes are simulation network partitions and process reboot/clog actions, which affect recovery, logging, and rollback behavior in the cluster.

## Dependencies And Integration Points
It depends on simulator APIs, `MasterInterface`, `ServerDBInfo`, log system configuration, commit proxy interfaces, and `FailureInjectionWorkload` scheduling. It cooperates with the general failure-injection framework through `initFailureInjectionMode`.

## Risks And Edge Cases
The workload skips injection when no tLogs or commit proxies are present, or when a proxy shares IP with a tLog that would be clogged. The member initializer `double meanDelay = 20.0, clogDuration = clogDuration = 3.0` is unusual and worth preserving carefully if edited. Aggressive clogging can interact with unrelated workloads unless they disable failure injection.

## Test Signals
Trace events `AttemptingToTriggerRollback` and `UnableToTriggerRollback` describe whether injection occurred. `check` always returns true; failures surface as cluster/test errors triggered by the injected rollback conditions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Rollback.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RyowCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/RyowCorrectness.cpp

## Purpose
`RyowCorrectnessWorkload` compares random read-your-writes transaction sequences against an in-memory key-value model. It validates that gets, ranges, selectors, key selectors, sets, clears, and range clears behave identically in an RYW transaction and the local `MemoryKeyValueStore`.

## Important APIs, Types, And Functions
The file defines an `Operation` struct with operation types `SET`, `GET`, `GET_RANGE`, `GET_RANGE_SELECTOR`, `GET_KEY`, `CLEAR`, and `CLEAR_RANGE`. `RyowCorrectnessWorkload` derives from `ApiWorkload` and registers as `RyowCorrectness`. Important methods are `generateOperationSequence`, `applySequenceToStore`, `applySequenceToDatabase`, `compareResults`, and `performTest`.

## Control Flow
Setup chooses the `READ_YOUR_WRITES` transaction factory. Each test loop generates a random sequence of `opsPerTransaction`, applies it to the memory store while collecting read results, applies the same sequence to a database transaction with retry handling, commits, then compares read outputs and final database contents against the memory model. The loop is wrapped in a timeout of `duration`.

## State And Persistence Behavior
The memory model in `ApiWorkload` tracks expected contents. Database mutations are committed transactionally. On `commit_unknown_result`, database read results already observed are retained and the transaction is retried without replacing them; on other retryable errors, collected results are cleared before `onError`.

## Dependencies And Integration Points
It depends on `ApiWorkload`, `MemoryKeyValueStore`, tester interface helpers such as `selectRandomKey`, `generateKeySelector`, `generateValue`, and `compareDatabaseToMemory`. It specifically exercises the transaction wrapper abstraction rather than raw `Transaction`.

## Risks And Edge Cases
The generated operation distribution weights reads and sets heavily but still covers selectors and range clears. Selector ranges normalize begin/end in the model when needed. The handling of `commit_unknown_result` is subtle because repeated reads could see different state; preserving first results is part of the correctness model.

## Test Signals
Failures call `testFailure` with either "Transaction results did not match" or "Database contents did not match" after printing the failed operation details. The workload has no metrics beyond inherited signals and `check` behavior from `ApiWorkload`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RyowCorrectness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/S3ClientWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/S3ClientWorkload.cpp

## Purpose
`S3ClientWorkload` validates FoundationDB blob/S3 client upload, download, delete, credential discovery, and optional mock-S3 fault injection in simulation. It uploads a generated credentials file to a blob URL, downloads it, compares bytes, and cleans local and remote artifacts.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `S3ClientWorkload`. Important methods are `setupCredentialsFile`, `addFileToUrl`, `start`, and `_setup`. It uses `copyUpFile`, `copyDownFile`, `deleteResource`, `S3BlobStoreEndpoint::fromString`, `MockS3Server`, `MockS3ServerChaos`, `S3FaultInjector`, global `INetwork::enBlobCredentialFiles`, and platform file helpers.

## Control Flow
Setup on client 0 registers a mock S3 HTTP handler when the URL points to localhost, optionally using the chaos server, and all clients configure fault rates when chaos is enabled. `start` runs only on client 0, disables bulk-loading connection failures in simulation, pre-cleans stale files, creates a deterministic per-run directory under `simfdb`, writes credentials, builds a unique object URL, uploads, downloads, deletes the remote object, compares downloaded content, then deletes local files and the run directory.

## State And Persistence Behavior
The workload writes a credentials JSON file in a per-run simulation directory and registers that path in network-global blob credential file state. It creates and deletes one remote S3 object. Local cleanup is best-effort after success and after upload failures.

## Dependencies And Integration Points
It integrates with FoundationDB's blobstore URL parser, backup/S3 credential handling, simulator HTTP handlers, mock S3 persistence, chaos fault injector, and platform filesystem APIs. It also disables a class of connection failures because network partitions between cluster controller and data distributor can prevent unrelated bulk-loading tasks from completing.

## Risks And Edge Cases
The URL manipulation must preserve resources and query strings; malformed base URLs throw `backup_invalid_url`. Cleanup errors are non-fatal except for the original transfer error. The `pass` field is initialized true and the destructor logs pass/fail, but the file does not set `pass=false` on caught errors before throwing, so destructor traces may not fully encode failure state.

## Test Signals
Transfer errors emit `S3ClientWorkloadError`, URL parse failures emit `S3ClientWorkloadURLParseError`, byte mismatches emit `S3ClientWorkloadContentMismatch`, and cleanup paths emit debug or warning traces. `check` returns true; actor failure is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/S3ClientWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SaveAndKill.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/SaveAndKill.cpp

## Purpose
`SaveAndKillWorkload` records enough simulation topology and restart metadata to an INI file, then reboots all non-excluded non-spawned processes and stops the simulator. It supports restart/restore simulation workflows.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SaveAndKill`. Important options are `restartInfoLocation`, `testDuration`, and `isRestoring`. The main logic is in `start`, using `CSimpleIni`, `g_simulator`, `FDBSimulationPolicyState`, `DatabaseConfiguration`, process locality, `INetworkConnections::convertMockDNSToString`, `SERVER_KNOBS`, and `FLOW_KNOBS`.

## Control Flow
Setup disables swaps to all. `start` waits a random fraction of `testDuration`, loads the restart INI, writes restore flags and metadata such as processes per machine, listeners per process, desired coordinators, connection string, tester count, TSS mode, mock DNS, and encryption/auth knob state. It gathers currently rebooting and active processes by data folder, writes machine and process address/data/coordination folder sections, saves the INI, reboots each process, yields for 100 zero-delay turns, and stops the simulator.

## State And Persistence Behavior
The main persistent output is the restart info INI file. It captures machine grouping, locality, process class, IP/port mappings, data folders, and coordination folders. Runtime state changes include process reboots and simulator stop. It disables all failure-injection workloads to reduce nondeterministic topology changes while snapshotting restart metadata.

## Dependencies And Integration Points
It integrates with restart tests, snapshot restore flows, simulator process metadata, connection-string policy state, mock DNS, encryption header token knobs, and SimpleIni. It filters out spawned KV processes and processes marked `excludeFromRestarts`.

## Risks And Edge Cases
`processCount` is written as `allProcessesMap.size() - 1`, which assumes one process should be excluded from the count. Process deduplication by data folder intentionally merges rebooting and active process records. Because it kills processes and stops simulation, it must run in scenarios expecting a restart boundary.

## Test Signals
`check` returns true. Correctness is observed indirectly by whether subsequent restart/restore phases can consume the generated INI and restart the simulated cluster.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SaveAndKill.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SelectorCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/SelectorCorrectness.cpp

## Purpose
`SelectorCorrectnessWorkload` stress-tests key selectors and range reads over a synthetic numeric keyspace. It validates direct `get` expectations and selector-bounded `getRange` result sizes, both with and without read-your-writes mutations.

## Important APIs, Types, And Functions
It derives from `TestWorkload` and registers as `SelectorCorrectness`. Important members are operation count bounds, `maxKeySpace`, `maxOffset`, `testReadYourWrites`, `transactions`, and `retries`. Core actors are `SelectorCorrectnessSetup` and `SelectorCorrectnessClient`.

## Control Flow
Setup writes even-numbered keys. In RYW mode it writes keys divisible by four and randomly writes keys congruent to two. The client repeatedly creates a native `Transaction` and a `ReadYourWritesTransaction`; in RYW mode it stages additional writes before reads. Each loop randomly performs either point get validation or selector range validation with randomized `onEqual`, offset, and reverse flags. It computes expected result size algebraically and compares actual range size below `maxKey`.

## State And Persistence Behavior
Setup persists the base key distribution. RYW-mode per-transaction writes are local to the `ReadYourWritesTransaction` and are not committed by the client loop. Native mode validates persisted even keys only. Transactions are reset after each operation batch.

## Dependencies And Integration Points
It uses NativeAPI transactions, `ReadYourWritesTransaction`, key selector APIs, tester workload metrics, and deterministic random key generation. It is an API semantics workload rather than a storage durability test.

## Risks And Edge Cases
The constructor appears to read `maxOperationsPerTransaction` from the `minOperationsPerTransaction` option key, which may unintentionally ignore a distinct max option. Error handling calls `trRYOW.onError(err)` even when native `tr` was used, so retry semantics are mostly relevant to the RYW transaction object. Expected-size arithmetic is compact and sensitive to selector boundary conventions.

## Test Signals
Failures emit `RanSelTestFailure` with reasons for missing/present values or range size mismatches. Metrics report transactions and retries. `check` clears clients and returns true, so severe trace events are the primary failure signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SelectorCorrectness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Serializability.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/Serializability.cpp

## Purpose
`SerializabilityWorkload` compares two executions of randomly generated transaction groups to detect violations in transactional serialization, RYW behavior, conflict handling, watches, atomic operations, and range/key reads.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `Serializability`. It defines `GetRangeOperation`, `GetKeyOperation`, `GetOperation`, and `TransactionOperation`. Important methods are `randomTransaction`, `runTransaction`, `getDatabaseContents`, `resetDatabase`, and `_start`.

## Control Flow
Client 0 repeatedly generates initial data and three random transactions `a`, `b`, and `c`. It first resets the database, runs and commits `a`, then `b`, then `c`, and captures contents. It resets again, runs `a` and `b` in a single transaction, runs `c` in another transaction, commits both, then compares final contents and all deterministic read futures. Snapshot reads in transaction `c` can be masked with `dontCheck` because they may legitimately differ across schedules.

## State And Persistence Behavior
Each iteration clears `normalKeys` and writes generated initial data before executing test schedules. Mutations include sets, range clears, single-key clears, atomic ops, explicit read/write conflict ranges, and watches. Reads are stored as futures so later comparisons observe the actual completed results.

## Dependencies And Integration Points
It depends on NativeAPI, `ReadYourWritesTransaction`, actor collections, tester workload helpers, mutation types, key selectors, and watch APIs. It exercises both read and write transaction paths with randomized waiting between operations.

## Risks And Edge Cases
The workload uses assertions for mismatches and does not set `success=false`, so assertion failure is the primary error path. Snapshot-read masking is intentionally selective; incorrect masking could hide or expose nondeterminism. Watch futures are created but not compared, serving mainly as operations affecting transaction behavior.

## Test Signals
Mismatches emit `SRL_ResultMismatch`, `SRL_Result1`, and `SRL_Result2` traces before asserting. The configuration trace reports node count, key layout, value sizes, and clear size. `check` returns the `success` flag, which remains true unless changed by future edits.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Serializability.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Sideband.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/Sideband.cpp

## Purpose
`SidebandWorkload` tests causal visibility when one client notifies another client through a sideband `RequestStream` after committing a key. The checker must be able to read the committed key after receiving the message.

## Important APIs, Types, And Functions
The file defines serializable `SidebandMessage` and `SidebandInterface`, then registers `SidebandWorkload`. Important methods are `persistInterface`, `fetchSideband`, `mutator`, and `checker`. It uses `RequestStream`, endpoint serialization via `BinaryWriter`/`BinaryReader`, native `Transaction`, and perf counters for messages and causal errors.

## Control Flow
Each client persists its sideband interface in `Sideband/Client/<clientId>`. The mutator fetches the next client's interface, periodically creates a random `Sideband/Message/<key>`, commits `deadbeef`, records the commit version, and sends the key/version to the other client. The checker waits on its own request stream and reads the corresponding key, emitting a causal consistency error if it is absent.

## State And Persistence Behavior
Interface endpoints and message keys are persisted in normal keyspace. Message keys are not cleaned up. The workload records when a random message key was unexpectedly already present and uses that read version as a conservative commit version.

## Dependencies And Integration Points
It integrates Flow request streams with database transaction causality, endpoint serialization, and multi-client workload setup. It relies on every client successfully persisting an interface before peers fetch it.

## Risks And Edge Cases
The workload assumes client IDs form a ring and that request stream delivery plus database commit visibility should be causally safe. Key collisions are tracked but rare. Client actor errors and consistency errors are checked only at the end of the timed run.

## Test Signals
`CausalConsistencyError` indicates a sideband notification was received before the committed key was readable. `TestFailure` is emitted for client actor errors or nonzero causal consistency errors. Metrics include messages, causal errors, and unexpectedly present keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Sideband.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SidebandSingle.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/SidebandSingle.cpp

## Purpose
`SidebandSingleWorkload` is a single-client variant of the sideband test focused on cached read versions. It validates that `USE_GRV_CACHE` does not return a too-stale result after a sideband signal, including `commit_unknown_result` cases.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SidebandSingle`. It uses a `PromiseStream<std::pair<uint64_t, Version>>` instead of serialized cross-client interfaces. Core actors are `mutator` and `checker`; the checker sets `FDBTransactionOptions::USE_GRV_CACHE` and initializes shared database state with `cx->initSharedState()`.

## Control Flow
Client 0 runs both actors. The mutator first writes `oldbeef` to a random message key with normal retries, then attempts to write `deadbeef` without retrying `commit_unknown_result`. On unknown result it sends the key with `invalidVersion`; otherwise it sends the committed version. The checker reads the key with GRV cache, requires it to exist, and if it sees a value other than `deadbeef`, compares against a non-cached read to distinguish a legitimately unknown commit result from stale cache behavior.

## State And Persistence Behavior
All state is in normal `Sideband/Message/<key>` keys plus the in-memory promise stream. Old and new values are intentionally written to the same key to create stale-read detection opportunities. Message keys are not removed.

## Dependencies And Integration Points
It depends on NativeAPI transactions, GRV cache transaction option support, shared database state initialization in simulation, and tester metrics. It complements `Sideband.cpp` by removing cross-client request stream serialization from the core GRV-cache test.

## Risks And Edge Cases
The unknown-result path intentionally allows reading `oldbeef` if the no-cache read agrees. If cached and uncached reads differ, it reports `CausalConsistencyError3`. The workload only runs on client 0, so multi-client causality is not covered here.

## Test Signals
`CausalConsistencyError1` reports missing keys, `CausalConsistencyError2` reports stale cached values without unknown-result allowance, and `CausalConsistencyError3` reports cache/no-cache disagreement. `DebugSidebandCheckError` and `DebugSidebandNoCacheError` expose retry paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SidebandSingle.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SimpleAtomicAdd.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/SimpleAtomicAdd.cpp

## Purpose
`SimpleAtomicAddWorkload` verifies basic `MutationRef::AddValue` behavior by applying a fixed number of atomic adds to one key and checking the final integer value.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SimpleAtomicAdd`. Important options are `addValue`, `iterations`, `initialize`, `initialValue`, `sumKey`, and `testDuration`. Core actors are `setInitialValue`, `applyAtomicAdd`, and `_check`.

## Control Flow
Only client 0 runs. `_start` optionally initializes `sumKey`, pushes `iterations` timeout-wrapped `applyAtomicAdd` futures, and calls `waitForAll(clients)`. Each add actor uses a `ReadYourWritesTransaction`, calls `atomicOp(sumKey, val, MutationRef::AddValue)`, and retries on errors. `_check` reads the key and compares it to `addValue * iterations + initialValue`.

## State And Persistence Behavior
The workload persists a little-endian integer byte representation at `sumKey`. Atomic adds are committed independently and concurrently. The check copies the stored bytes into a `uint64_t`, defaulting to zero when absent.

## Dependencies And Integration Points
It depends on NativeAPI, `ReadYourWritesTransaction`, generic actor timeout helpers, and FoundationDB atomic mutation semantics. It is a narrow sanity workload for atomic addition.

## Risks And Edge Cases
The `_start` actor calls `waitForAll(clients)` without `co_await` or returning it, which means the start actor can finish before client futures complete. Timeouts still wrap individual add actors, but lifecycle expectations depend on actor retention in the `clients` vector and later `check`. Integer width and signedness are also notable: `addValue` is an `int`, while expected and actual are compared as `uint64_t`.

## Test Signals
Trace events `SAABegin`, `SAASetInitialValue`, and `SAACheckEqual` show operations and final comparison. `_check` returns false on mismatch; setup/add/check retry errors emit corresponding `SAA*Error` traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SimpleAtomicAdd.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SkewedReadWrite.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/SkewedReadWrite.cpp

## Purpose
`SkewedReadWriteWorkload` extends `ReadWriteCommon` to concentrate read and optional write traffic on shards owned by rotating subsets of storage servers. It creates server-local hot spots and records read/write latency under skewed placement-aware load.

## Important APIs, Types, And Functions
It derives from `ReadWriteCommon` and registers as `SkewedReadWrite`. Important state includes `hotServerFraction`, `hotServerShardFraction`, `hotServerReadFrac`, `hotServerWriteFrac`, `hotReadWriteServerOverlap`, `serverShards`, `serverInterfaces`, and `currentHotRound`. Core methods are `updateServerShards`, `convertKeyBoundaryToIndexShard`, `setHotServers`, `getRandomKeyFromHotServer`, `getRandomKey`, `readOp`, `startReadWriteClients`, and `randomReadWriteClient`.

## Control Flow
`start` optionally starts latency tracing, builds the current storage-server-to-index-range map by reading system server lists and server key ranges, then runs `skewRound` rounds. Each round chooses a contiguous rotating set of hot servers, starts read/write client actors for the round duration, clears clients, waits five seconds, and refreshes shard ownership. Clients issue Poisson-paced transactions, choose reads and writes from hot or uniform key distributions, measure GRV/read/commit/total latency, and retry on errors.

## State And Persistence Behavior
The workload writes values through ordinary read/write transactions inherited from `ReadWriteCommon`. It reads system keyspace with `READ_SYSTEM_KEYS` to derive shard placement. Hot server state is in-memory and recomputed between rounds. Metrics and latency sketches are updated during transactions.

## Dependencies And Integration Points
It depends on `ReadWriteWorkload`, `BulkSetup`, `WorkerInterface`, server key system ranges, storage server interface decoding, `RunRYWTransaction`, latency metric helpers, and `TDMetric`. It includes a unit test for `keyForIndex`/`indexForKey` round-tripping.

## Risks And Edge Cases
`convertKeyBoundaryToIndexShard` asserts that every shard range contains at least one workload key in both forward and reverse reads; empty shards in the workload range would assert. `hotServerCount` is `ceil(fraction * serverShards.size())`, so an empty `serverShards` vector would be invalid. Traffic skew depends on current shard map consistency and can be disrupted by data movement.

## Test Signals
Metrics inherited from `ReadWriteCommon` include read, commit, GRV, retry, transaction class, and latency signals. The unit test `/KVWorkload/methods/ParseKeyForIndex` asserts index parsing correctness for normal and non-overlapping key encodings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SkewedReadWrite.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SlowTaskWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/SlowTaskWorkload.cpp

## Purpose
`SlowTaskWorkload` stress-tests the slow task profiler or Flow profiler by repeatedly doing expensive exception unwinding in a tight loop while profiling is enabled.

## Important APIs, Types, And Functions
It derives from `TestWorkload` and registers as `SlowTaskWorkload`. The important methods are `start`, static actor `go`, and non-actor helper `do_slow_exception_thing`. It uses `setupRunLoopProfiler`, `SignalSafeUnwind` counters, `dl_iterate_phdr_calls`, and `fmt::print`.

## Control Flow
`start` enables the run loop profiler and returns `go`. `go` waits one second, snapshots profiler counters, then for ten one-second intervals repeatedly calls `do_slow_exception_thing`, which throws and catches `success()` one thousand times per call. At completion it prints exception and profiler counter deltas to stderr.

## State And Persistence Behavior
There is no database state. The workload mutates profiler/runtime counters and produces stderr output.

## Dependencies And Integration Points
It depends on Flow profiling and signal-safe unwind infrastructure. The helper is deliberately non-actor so actual exception unwinding occurs, making it a runtime/profiler stressor rather than a database workload.

## Risks And Edge Cases
This workload intentionally burns CPU and throws large numbers of exceptions. It can perturb timing-sensitive simulations and should be used only where slow-task profiling behavior is the target.

## Test Signals
The printed summary reports exception count, `dl_iterate_phdr` call delta, profiles disabled, profiles overflowed, and profiles captured. `check` always returns true.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SlowTaskWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SnapTest.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/SnapTest.cpp

## Purpose
`SnapTestWorkload` orchestrates snapshot creation and validation across restart phases. Different `testID` values create pre-snapshot keys, take a snapshot, create post-snapshot keys, validate restored state, or test rejection of a non-whitelisted snapshot command.

## Important APIs, Types, And Functions
It derives from `TestWorkload` and registers as `SnapTest`. Important state includes `numSnaps`, `maxSnapDelay`, `testID`, `snapUID`, `restartInfoLocation`, `retryLimit`, `snapSucceeded`, and `attemptDuplicateSnapshot`. Key actors are `_create_keys` and `_start`, using `snapCreate`, `CSimpleIni`, `SERVER_KNOBS->SNAP_MINIMUM_TIME_GAP`, and normal-key range scans.

## Control Flow
Only client 0 runs. For `testID=0`, it writes 1000 even `snapKey` entries. For `testID=1`, it waits a random delay, calls `/bin/snap_create.sh` with a random UID, optionally submits a duplicate snapshot request, retries according to `retryLimit`, and stores `RestoreSnapUID` plus `BackupFailed` in restart info. For `testID=2`, it writes 1000 odd entries after the snapshot. For `testID=3`, it skips validation if snapshot failed, otherwise scans `normalKeys` and verifies all `snapKey` IDs are even and value-equal. For `testID=4`, it verifies a non-whitelisted path fails.

## State And Persistence Behavior
The workload writes `snapKey*` records into normal keyspace and writes snapshot metadata to the restart INI file. It also modifies simulation policy by disabling log set kills. Snapshot data is external to normal transactions and consumed by later restart phases.

## Dependencies And Integration Points
It integrates with ManagementAPI snapshot creation, restart metadata, simulation policy, SimpleIni, and tester failure-injection controls. It disables `RandomMoveKeys` and `Attrition` because data movement and missing machines can make snapshot state incomplete.

## Risks And Edge Cases
Only `numSnap=1` validation is noted as currently supported. Duplicate snapshot handling expects either duplicate request behavior or the latest request to complete. Snapshot creation can fail for many reasons, so retries may run indefinitely when `retryLimit=-1`. Validation assumes exactly 1000 pre-snapshot keys and no odd post-snapshot keys after restore.

## Test Signals
`SnapshotCreateStatus` records success or failure. `check` returns `snapSucceeded` for `testID=1`. Restore validation failures emit `SnapTestVerifyCntValue` or throw `operation_failed`; unsupported path tests assert expected snapshot errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SnapTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SpecialKeySpaceCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/SpecialKeySpaceCorrectness.cpp

## Purpose
`SpecialKeySpaceCorrectnessWorkload` validates special key space read/write semantics, error handling, conflict range reporting, management commands, and metrics schemas. It creates test-only special key ranges, mirrors them through a RYW transaction, and compares direct special-key results to reference transaction results.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SpecialKeySpaceCorrectness`. Important methods include `_setup`, `testRywLifetime`, `getRangeCallActor`, `compareRangeResult`, `randomRWKeyRange`, `testSpecialKeySpaceErrors`, `testConflictRanges`, `managementApiCorrectnessActor`, and `metricsApiCorrectnessActor`. It uses `SpecialKeySpace`, `SKSCTestRWImpl`, `SKSCTestAsyncReadImpl`, `ReadYourWritesTransaction`, `FDBTransactionOptions::RAW_ACCESS`, `SPECIAL_KEY_SPACE_RELAXED`, `SPECIAL_KEY_SPACE_ENABLE_WRITES`, management API command prefixes, JSON schemas, and system keys.

## Control Flow
Setup creates a fresh `SpecialKeySpace`, configures a RYW transaction at version 100, registers random test-only read/write or async-read ranges, and populates random keys. `start` runs a lifetime cancellation test, then concurrently runs special-key error tests, randomized getRange comparison, read and write conflict range comparison, and metrics schema validation for `testDuration`. Client 0 additionally runs management API correctness that changes coordinators when possible, verifies maintenance and data-distribution special keys, disables/re-enables DD-related settings, and checks underlying system keys.

## State And Persistence Behavior
Most test-only special-key state is in a local RYW transaction and `SpecialKeySpace` module implementations. Management API tests can durably change coordinators, maintenance/DD mode, healthy-zone, rebalance ignore state, and then restore/clear those changes. Conflict range tests manipulate transaction conflict metadata exposed through special keys.

## Dependencies And Integration Points
It depends on global config, ManagementAPI, NativeAPI, ReadYourWrites, Schemas, SpecialKeySpace modules, server knobs, tester interfaces, and system data ranges. It disables all failure injection workloads because cluster health and configuration stability are prerequisites for deterministic management API validation.

## Risks And Edge Cases
The workload intentionally covers many tricky boundary conditions: cross-module reads, relaxed reads, no-module errors, selector clamping, special-key write-disabled errors, cross-module clears, legal range bounds, RYW-disabled conflict range behavior, committed write conflict range reads, and worker interface reads. Management tests can alter real cluster configuration and must reliably revert coordinator and DD changes.

## Test Signals
`wrongResults` must remain zero for `check` to pass. Failures emit `TestFailure` details for range flag/size/key/value mismatches, conflict range mismatches, out-of-order results, schema failures, and unexpected management API responses. Metrics schema validation uses `schemaMatch` against `faultToleranceStatusSchema`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SpecialKeySpaceCorrectness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SpecialKeySpaceRobustness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/SpecialKeySpaceRobustness.cpp

## Purpose
`SpecialKeySpaceRobustnessWorkload` exercises management special-key APIs in scenarios that can run under failure injection. It focuses on idempotency, error schema validity, locking behavior, consistency-check toggles, coordinator reads, advance-version behavior, and conflict ranges for DD mode changes.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SpecialKeySpaceRobustness`. Important helpers are `getRangeResultInOrder`, `runExcludeAndGetVersionKey`, and `managementApiCorrectnessActor`. It uses `SpecialKeySpace::getManagementApiCommandPrefix`, `getManagementApiOptionsSet`, `getWorkers`, `JSONSchemas::managementApiErrorSchema`, database lock keys, consistency-check keys, coordinator keys, `advanceversion`, DD mode keys, and move-keys lock keys.

## Control Flow
Only client 0 runs. The actor first writes all management options and checks ordered range output. It verifies invalid `exclude` writes produce schema-valid errors, tests repeated exclude/failed commands only update version keys once, validates `setclass` reads/RYW behavior and invalid class errors, checks class source updates, locks the database and verifies normal reads fail with `database_locked`, unlocks, toggles consistencycheck off and back on, reads coordinators through special keys, forces advance version until read versions exceed the target, and proves DD mode writes conflict with transactions reading move-key lock keys.

## State And Persistence Behavior
The workload writes management command special keys that translate into system metadata changes: exclusions, failed lists, process class source, database lock state, consistency-check suspend state, coordinator-derived reads, advance-version recovery, and DD mode updates. It carefully clears lock and consistencycheck state before completion.

## Dependencies And Integration Points
It depends on ManagementAPI, ReadYourWrites, Schemas, SpecialKeySpace, system metadata keys, worker discovery, cluster connection strings, and lock-aware/raw/special-write transaction options. Unlike the correctness workload, it is intended to tolerate some retriable errors from failure injection.

## Risks And Edge Cases
The workload performs real management actions, so cleanup is critical. It handles `commit_unknown_result`, already locked database, empty worker lists, process reboot changing class source back to command-line, and transient GRV/throttling errors. Advance-version expects commit failure while recovery advances the cluster version.

## Test Signals
Assertions and `TestFailure` traces flag ordering or semantic violations. Debug traces identify unexpected special-key API errors, lock/unlock failures, setclass/exclude cases, advance-version progress, and DD conflict behavior. `check` returns true, so actor assertions/errors are the practical failure signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/SpecialKeySpaceRobustness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/StatusWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/StatusWorkload.cpp

## Purpose
`StatusWorkload` repeatedly fetches cluster status JSON, optionally validates it against a schema, optionally mutates latency-band configuration, and records status latency and response-size metrics.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `Status`. Important members are `testDuration`, `requestsPerSecond`, `maxAcceptableStatusLatency`, `enableLatencyBands`, `parsedSchema`, counters, and `worstLatency`. Key functions are `schemaCoverageRequirements`, `generateBands`, `configureLatencyBands`, and `fetcher`. The file also contains unit test `/fdbserver/status/schema/basic`.

## Control Flow
The constructor parses the requested status schema and registers schema coverage requirements. Setup may start `configureLatencyBands`, which writes randomized latency band configuration under `latencyBandConfigKey` using system-key and lock-aware options. Client 0 runs `fetcher` for `testDuration`, issuing Poisson-paced `StatusClient::statusFetcher` calls, serializing replies to measure size, tracking worst latency, and validating the JSON object against the parsed schema.

## State And Persistence Behavior
The workload can persist latency band configuration in system keyspace. It otherwise reads status data and maintains in-memory counters. The schema coverage hooks affect test coverage accounting rather than database state.

## Dependencies And Integration Points
It depends on `StatusClient`, JSON schema helpers, ManagementAPI system keys, `flow/UnitTest`, and status schemas from `fdbclient/Schemas.h`. The unit test exercises `schemaMatch` behavior for objects, arrays, enums, maps, type mismatches, and unexpected fields.

## Risks And Edge Cases
If schema validation fails, the workload logs `StatusWorkloadValidationFailed` but does not increment `errors`, so final `check` only fails on fetch errors or excessive latency. Latency-band configuration can continue independently and returns randomly after one or more writes.

## Test Signals
Metrics include requests, replies, average reply size, errors, and worst latency. Failure signals include `StatusWorkloadError`, `StatusWorkloadValidationFailed`, `StatusLatencyExceeded`, and schema coverage exceptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/StatusWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/StorageCorruption.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/StorageCorruption.cpp

## Purpose
`StorageCorruptionWorkload` is a negative test for storage corruption detection. It enables a `StorageCorruptionBug`, disables data distribution, lets corruption injection run, then re-enables data distribution and expects consistency checking to report failure.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `StorageCorruption`. Important members are `std::shared_ptr<StorageCorruptionBug> bug`, `SimBugInjector bugInjector`, and `testDuration`. `_start` uses `setDDMode`, bug injector enable/disable, `bug->corruptionProbability`, `bug->numHits`, and `ProcessEvents::uncancellableEvent`.

## Control Flow
The constructor enables the storage corruption bug in the local injector, configures corruption probability, and disables the injector. Client 0 disables DD with `setDDMode(cx, 0)`, enables corruption injection for `testDuration`, sets probability to zero, logs the number of corruption hits, disables injection, registers an uncancellable process event listener for severe `ConsistencyCheckFailure`, and re-enables DD.

## State And Persistence Behavior
The workload intentionally corrupts storage-server state through the bug injector and toggles data distribution mode. It does not write ordinary keys directly. Its success condition is detecting the induced corruption when consistency checking resumes.

## Dependencies And Integration Points
It depends on `StorageCorruptionBug`, `SimBugInjector`, `ManagementAPI::setDDMode`, and `ProcessEvents`. It disables all failure-injection workloads to isolate the corruption signal.

## Risks And Edge Cases
The workload returns true from `check` regardless of whether consistency failure was observed. The positive signal is a trace-event side effect (`NegativeTestSuccess`) registered after corruption injection. If no corruption hits occur during `testDuration`, the negative test may not exercise the target path.

## Test Signals
`CorruptionInjections` reports `bug->numHits()`. A severe `ConsistencyCheckFailure` process event triggers `NegativeTestSuccess`. Actor errors during DD mode changes or bug injection surface as workload failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/StorageCorruption.cpp -->

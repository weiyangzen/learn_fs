# subset-b-008489 Research

Grouped code research for FoundationDB tester workloads under `fdbserver/workloads`. Each section is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BackupWorkload.cpp

## Purpose
`BackupWorkload.cpp` defines the tester workload named `Backup`. It exercises FoundationDB's file backup path from simulation by submitting a backup over `normalKeys`, optionally using differential backup mode, pause/resume behavior, backup abort/discontinue paths, and test encryption-key files. A separate workload handles restore, so this file focuses on creating a restorable backup and validating the backup agent status path.

## Important APIs, Types, And Functions
The main type is `BackupWorkload : TestWorkload`, registered with `WorkloadFactory<BackupWorkload>`. It uses `FileBackupAgent`, `BackupAgentBase`, `IBackupContainer`, `BackupDescription`, `BackupContainerFileSystem::createTestEncryptionKeyFile`, `MutationLogType`, and `LockDB`. Key actors are `changePaused`, `resumeAgent`, `statusLoop`, `doBackup`, and `_start`.

## Control Flow
Only client 0 runs `start`. The constructor derives randomized timing options such as `backupAfter`, `restoreAfter`, `abortAndRestartAfter`, `differentialBackup`, and `stopDifferentialAfter`, then restricts backup ranges to `normalKeys`. `_start` may launch a pause toggler, creates an encryption key file when requested, waits for `backupAfter`, and calls `doBackup`. `doBackup` optionally aborts stale/duplicate backup state, submits a `file://simfdb/backups/` backup, runs a status loop, optionally waits until a differential backup is restorable before discontinuing or aborting, then waits for final backup completion.

## State And Persistence
Persistent effects are backup metadata in FDB system keys and backup files under the simulated filesystem. If encryption is enabled, a simulated encryption key file under `simfdb/` is created and passed to the backup agent. Workload state is otherwise in actor-local timing fields, backup tag/ranges, the pause actor, and trace events.

## Dependencies And Integration Points
The workload integrates with `fdbclient/BackupAgent.h`, backup containers, simulated filesystem backup containers, tester workload registration, `SERVER_KNOBS`, deterministic/nondeterministic randomness, and simulation backup-agent policy. It is meant to run with backup agents available and to coexist with a restore-oriented workload that consumes the produced backup.

## Risks
The status loop is intentionally infinite and relies on actor cancellation through owning futures. Randomized abort/discontinue paths can expose `backup_unneeded`, `backup_duplicate`, and `database_locked` races. Timing values must remain coherent; `stopDifferentialAfter` is computed relative to backup/abort/restore timing. Encryption tests depend on local simulated file setup. A local shadow variable named `minBackupAfter` means the member field is not populated, though the member is not subsequently used.

## Test Signals
Useful signals are `BW_Param`, `BW_DoBackupSubmitBackup`, `BW_DoBackupWaitForRestorable`, `BW_LastBackupContainer`, `BW_NotRestorable`, `BW_DoBackupComplete`, and `BackupCorrectness` errors. Successful workload `check` always returns true, so correctness is primarily encoded in trace/assert paths and later restore validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BackupWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BulkDumping.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BulkDumping.cpp

## Purpose
`BulkDumping.cpp` defines `BulkDumpingWorkload`, an end-to-end simulation test for exporting data with bulk dump and importing it with bulk load. It creates known random data, dumps a selected range to a filesystem or blobstore root, clears database and bulk metadata, reloads a selected range from the dump output, checks loaded data against the original dataset, and validates bulk load job history.

## Important APIs, Types, And Functions
The workload uses `BulkDumpState`, `BulkLoadJobState`, `BulkLoadTaskState`, `BulkLoadTransportMethod`, `createBulkDumpJob`, `submitBulkDumpJob`, `getSubmittedBulkDumpJob`, `setBulkDumpMode`, `createBulkLoadJob`, `submitBulkLoadJob`, `getRunningBulkLoadJob`, `cancelBulkLoadJob`, `acknowledgeAllErrorBulkLoadTasks`, and range-lock helpers such as `registerRangeLockOwner`. Mock S3 integration comes from `MockS3Server`, `MockS3ServerChaos`, and `S3FaultInjector`.

## Control Flow
`setup` optionally registers/configures a mock S3 server on client 0 for blobstore tests. `start` runs only on client 0, clears mock storage for blobstore simulation, disables connection failures, selects a dump range, writes 1000 ordered KVs, registers the bulk-load range-lock owner, enables bulk dump mode, submits a dump job, waits for no submitted dump job, clears data and bulk metadata, enables bulk load mode, submits a load job over either the dump range or a random range, waits for completion/error/cancellation, compares loaded KVs when range coverage is valid, acknowledges error tasks, validates job history, and removes the range-lock owner.

## State And Persistence
The workload writes normal keyspace data, system-key bulk dump and load metadata, range-lock owner state, job history, and filesystem/blobstore objects under `simfdb/bulkdump` or `jobRoot`. `clearDatabase` intentionally clears `normalKeys`, `bulkDumpKeys`, `bulkLoadJobKeys`, `bulkLoadTaskKeys`, and `bulkLoadJobHistoryKeys` before reloading.

## Dependencies And Integration Points
This test exercises the public bulk dump/load client APIs, DD mode toggles, KRM-backed task state, bulk-load range locking, the simulator, and optional mock S3 handlers. It disables workloads that race on DD mode, storage movement/corruption, validation, and random range locking.

## Risks
The job wait loops include timeout fallbacks that can proceed with intermediate task states, so a timeout-heavy run can validate partial state rather than full completion. Cancellation is currently disabled by forcing `maxCancelTimes = 0` because job IDs are random. Range coverage matters: if the load range is not contained by the dump range, data comparison is skipped and the expected result shifts to job-history error validation. Mock S3 handler reuse and chaos options can leak cross-test state if cleanup is incomplete.

## Test Signals
Important traces include `BulkDumpingWorkLoadSetKey`, `BulkDumpingWorkLoadDumpJobTimeout`, `BulkDumpingWorkLoadJobTimeout`, `BulkDumpingWorkLoadBulkLoadTaskWrongPhase`, `BulkDumpingWorkLoadError`, `BulkDumpingWorkLoadSetDumpModeFailed`, `BulkDumpingWorkLoadSetLoadModeFailed`, and mock S3 registration/chaos traces. The explicit `ASSERT`s around range locks, job history, and data equality are the primary pass/fail signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BulkDumping.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BulkLoad.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BulkLoad.cpp

## Purpose
`BulkLoad.cpp` defines a lightweight throughput workload named `BulkLoad`. It is not the metadata-driven bulk loading test; instead it continuously writes formatted keys and fixed-size values with many actors to measure raw write throughput, retries, and latency.

## Important APIs, Types, And Functions
The main type is `BulkLoadWorkload : TestWorkload`, registered by `WorkloadFactory<BulkLoadWorkload>`. It uses `Transaction`, `tr.set`, `tr.makeSelfConflicting`, `tr.getReadVersion`, `tr.commit`, `tr.onError`, `timeout`, `waitForAll`, `PerfIntCounter`, and `DDSketch<double>` for latency statistics.

## Control Flow
The constructor reads `testDuration`, `actorCount`, `writesPerTransaction`, `valueBytes`, `targetBytes`, and `keyPrefix`. `start` launches `actorCount` `bulkLoadClient` actors per tester client, each bounded by `testDuration`. Each actor repeatedly constructs a transaction containing `writesPerTransaction` sequential keys under `keyPrefix/bulkload/<client>/<actor>/<idx>`, makes the transaction self-conflicting, obtains a read version, commits, records latency and counters, and stops once its share of `targetBytes` has been exceeded.

## State And Persistence
Persistent state is user key data under the configured prefix. Runtime state is counters, retry counts, DDSketch samples, per-actor `idx`, and per-actor `totalBytes`. `check` clears the retained future vector but does not validate or remove written keys.

## Dependencies And Integration Points
The workload depends on the native client API, tester workload registration, `fdbrpc/DDSketch.h`, and FDB transaction conflict/read-version behavior. The formatted key pattern makes it easy to isolate throughput data by client and actor.

## Risks
The `targetBytes` comparison divides by `clientCount * actorCount`, so unusual zero/invalid option values would be unsafe, though defaults are positive. `valueBytes` is forced to at least 16 but metrics approximate bytes as `valueBytes + 16`, which does not include the full formatted key length. There is no correctness check for all expected rows, so failures are observed through transaction errors, retries, timeout, and metrics rather than data reconciliation.

## Test Signals
Metrics include transactions, retries, rows written, transactions/sec, rows/sec, keys/sec, bytes/sec, mean latency, median latency, 90th percentile, and 98th percentile. High retry counts or low throughput are the main workload-level signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BulkLoad.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BulkLoading.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BulkLoading.cpp

## Purpose
`BulkLoading.cpp` defines `BulkLoadingWorkload`, a simulation correctness test for low-level bulk load task submission, execution, metadata finalization, and range-lock cleanup. It generates SST files locally, submits bulk-load task states, toggles bulk-load mode, waits for task completion or error, compares loaded data, and ensures KRM metadata is cleared.

## Important APIs, Types, And Functions
Key types are `BulkLoadTaskTestUnit`, `BulkLoading : TestWorkload`, `BulkLoadTaskState`, `BulkLoadFileSet`, `BulkLoadByteSampleSetting`, and `KeyRangeMap<Optional<BulkLoadTaskTestUnit>>`. Important helpers include `clearAllBulkLoadTask`, `submitBulkLoadTask`, `finalizeBulkLoadTask`, `checkAllTaskCompleteOrError`, `checkBulkLoadMetadataCleared`, `generateSSTFiles`, `generateBulkLoadTaskUnit`, `simpleTest`, `complexTest`, and `backgroundWriteTraffic`.

## Control Flow
Only client 0 executes `start`. The workload disables simulation connection failures, optionally initializes all bulk-load task metadata to empty task values, may start background writers, registers the bulk-load range-lock owner, and then randomly selects `simpleTest` or `complexTest`. `simpleTest` submits two non-overlapping tasks over fixed ranges, enables bulk-load mode, waits for completion/error, disables mode to check data, re-enables mode to finalize tasks and acknowledge errors, then waits for metadata cleanup. `complexTest` submits three random possibly overlapping tasks, sometimes waits midstream and toggles mode, tracks outdated subranges in a `KeyRangeMap`, verifies only complete non-error data, finalizes tasks, and checks locks are released.

## State And Persistence
The workload writes generated SST and byte-sample SST files under `simfdb/bulkload/<index>`, bulk-load task metadata under system KRM ranges, range-lock owner records, loaded normal-key data, and optional background traffic. Metadata cleanup is validated by reading `bulkLoadTaskPrefix` over `normalKeys`.

## Dependencies And Integration Points
Dependencies include `fdbclient/BulkLoading.h`, `BulkLoadUtil`, `RocksDBCheckpointUtils`, `StorageMetrics`, range locks, DD bulk-load mode, RocksDB SST writers, byte-sampling helpers, and tester/simulator infrastructure. The file directly exercises server-side bulk-load task state transitions without going through a dump job.

## Risks
The generated file set initially uses an empty manifest name and relies on simulation assumptions. Background traffic futures are created in a local vector and not awaited, so they exist only as fire-and-forget actors during the test scope. Overlapping ranges deliberately create outdated task fragments; correctness depends on ignoring outdated and error ranges consistently. `checkBulkLoadMetadataCleared` has special expectations when metadata was preinitialized. Range-lock leaks would affect later workloads, so owner removal and `findExclusiveReadLockOnRange` assertions are important.

## Test Signals
Trace signals include `BulkLoadingSubmitBulkLoadTask`, `BulkLoadingWorkLoadIncompleteTasks`, `BulkLoadingWorkLoadFailedTasks`, `BulkLoadingDataProduced`, `BulkLoadingWorkLoadDataWrong`, `BulkLoadingWorkLoadSimpleTestComplete`, and `BulkLoadingWorkLoadComplexTestComplete`. Primary pass/fail signals are `ASSERT`s for data equality, metadata cleanup, task phases, and empty range locks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BulkLoading.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BulkSetup.h -->
# sources/storage-engines/foundationdb/fdbserver/workloads/BulkSetup.h

## Purpose
`BulkSetup.h` provides reusable templated setup helpers for workloads that need to populate large key ranges. It partitions a logical node/key index space across clients, creates range insertion jobs, writes generated key-value pairs with controlled conflict behavior and optional rate limiting, tracks insertion milestones, and optionally waits for data distribution to settle or warms the database.

## Important APIs, Types, And Functions
The header defines the `hasAuthToken` SFINAE helper and `setAuthToken`, allowing workloads with a `setAuthToken(Transaction&)` method to opt into authenticated transactions. Core actors are `checkRangeSimpleValueSize`, `setupRange`, `setupRangeWorker`, `trackInsertionCount` (declared here), `waitForLowInFlight`, and `bulkSetup`. The template parameter `T` is expected to expose `operator()(uint64_t)`, `keyForIndex`, `clientId`, `clientCount`, `description`, and optionally `dbInfo`.

## Control Flow
`bulkSetup` computes each client's node slice, optionally short-circuits if first/last keys are already present, smears start time, estimates a range size targeting about 10 KB per insertion transaction, builds shuffled range jobs, and launches 40 `setupRangeWorker` actors. Each worker pops jobs, calls `setupRange`, periodically persists `keycount|client|actor` and `bytesstored|client|actor`, and rate-limits by delaying until the computed next start. After all workers and optional insertion tracking complete, `bulkSetup` sends setup timing/rates, optionally waits for low data-in-flight, and optionally runs `databaseWarmer`.

## State And Persistence
Persistent state is the generated data plus optional progress keys `keycount|...` and `bytesstored|...`. `setupRange` writes all keys blind with `AddConflictRange::False` after adding one write conflict range over the whole generated span. If `valuesInconsequential` is true, it may treat existing first/last keys as enough evidence that the range is already loaded.

## Dependencies And Integration Points
The helpers use native transactions, tester workload utilities, `QuietDatabase`/`databaseWarmer`, `getDataInFlight`, simulation speed-up flags, auth token hooks, and deterministic randomness. They are shared by workload files that generate repeatable key/value records via a workload object.

## Risks
`jobs` is a shared vector popped by many actors in the same Flow thread model; it relies on cooperative actor scheduling rather than external locking. In speed-up simulation mode, existence reads are skipped to avoid `transaction_too_old`, which means blind writes may repeat existing data. The simple first/last presence check can produce false positives when interior data is missing. `waitForLowInFlight` can time out or surface attribute lookup errors depending on DD initialization.

## Test Signals
Trace events include `BulkSetupStart`, `<description>SetupStart`, `BulkSetupRangeAlreadyPresent`, `BulkRangeNotFound`, `CheckRangeError`, `BulkSetupFailed`, `SetupLoadComplete`, `DynamicWarming`, `DynamicWarmingDone`, and `<description>SetupOK`. Consumers typically use the `setupTime` and `ratesAtKeyCounts` promises as workload metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/BulkSetup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/workloads/CMakeLists.txt

## Purpose
This CMake file builds all workload sources in `fdbserver/workloads` into the static library target `fdbserver_workloads`. It is the build integration point that makes workload implementations available to the FoundationDB tester/server build.

## Important APIs, Types, And Functions
The file uses `fdb_find_sources(FDBSERVER_WORKLOADS_SRCS)`, `add_flow_target(STATIC_LIBRARY NAME fdbserver_workloads SRCS ...)`, `configure_fdbserver_common_includes`, `target_include_directories`, and `target_link_libraries`.

## Control Flow
CMake discovers workload sources, creates the static library, applies common fdbserver include settings, adds the workload directory as a private include path, and links the target privately against required fdbserver components.

## State And Persistence
There is no runtime state. Build output is the `fdbserver_workloads` static library and dependency graph entries generated by CMake.

## Dependencies And Integration Points
The workload library links with `fdbserver_consistencyscan`, `fdbserver_core`, `fdbserver_kvstore`, `fdbserver_worker`, `fdbserver_tester`, `fdbserver_datadistributor`, `fdbserver_resolver`, `fdbserver_storageserver`, and `fdbserver_mocks3`. Those dependencies match the broad set of workload code that reaches into server internals, consistency scans, storage engines, and mock S3.

## Risks
Because `fdb_find_sources` discovers all sources in the directory, adding a new workload source may automatically enter this target. Missing a required library dependency will surface as link errors rather than compile errors. Conversely, the broad private link set can hide unnecessary coupling between workloads and server internals.

## Test Signals
The relevant signal is a successful configure/build/link of `fdbserver_workloads` and downstream targets that consume it. Build failures after adding a workload usually point to source discovery, missing include directories, or missing private link dependencies here.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ChangeConfig.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ChangeConfig.cpp

## Purpose
`ChangeConfig.cpp` defines the `ChangeConfig` workload. It waits for a configurable delay, then changes the database configuration and/or coordinator set, including simulated extra databases. It specifically exercises management API configuration strings and special-key coordinator commands, including auto-coordinator discovery and error-schema validation.

## Important APIs, Types, And Functions
The core type is `ChangeConfigWorkload : TestWorkload`, with helpers `getConfigMode`, `configureExtraDatabase`, `configureExtraDatabases`, `changeConfigClient`, and `coordinatorsChangeActor`. It uses `ManagementAPI::changeConfig`, `waitForFullReplication`, simulated extra database creation, `SpecialKeySpace`, `JSONSchemas::managementApiErrorSchema`, `schemaMatch`, and `ReadYourWritesTransaction`.

## Control Flow
Only client 0 runs. After a random delay in `[minDelayBeforeChange, maxDelayBeforeChange]`, `changeConfigClient` may configure extra databases first or last. For the main database, it optionally applies `startingDisabledConfiguration` in simulation, waits for full replication, strips `"new "` from config modes when applying to an existing DB, and calls `changeConfig`. If coordinator changes are requested, it runs one or more `coordinatorsChangeActor` iterations, with repeated changes only for `"auto"`.

## State And Persistence
Persistent state includes cluster configuration changes, coordinator connection-string changes, and extra database configuration/coordinator state in simulation. The coordinator actor writes management special keys and expects the management special-key API to report command completion/failure through the error message module.

## Dependencies And Integration Points
The workload depends on the management API, special-key management modules, schema validation, `fdbrpc/simulator.h`, simulation policy extra databases, and tester workload failure-injection controls. It disables all failure-injection workloads because cluster configuration and coordinator changes are intentionally disruptive.

## Risks
Coordinator special-key writes are expected to throw `special_keys_api_failure`; the code asserts after a successful commit, so behavior changes in the API contract would fail the workload. Auto-coordinator selection can initially fail with retriable errors and only retries a bounded path. Misconfigured network addresses or insufficient machines can make the management API return schema-validated failures rather than apply changes. Extra database configuration is simulation-only and may race with main database changes.

## Test Signals
Trace events include `WaitForReplicas`, `WaitForReplicasExtra`, `GetAutoCoordinatorsChange`, `CoordinatorsChangeBeforeCommit`, and `CoordinatorsChangeError`. The workload `check` returns true, so failures are via assertions, thrown management errors, or schema mismatches.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ChangeConfig.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/CheckMetadataEncoding.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/CheckMetadataEncoding.cpp

## Purpose
`CheckMetadataEncoding.cpp` defines `CheckMetadataEncodingWorkload`, which validates whether `keyServers` and `serverKeys` metadata use old or shard-encoded formats according to `SERVER_KNOBS->SHARD_ENCODE_LOCATION_METADATA`. It is intended for forward migration and rollback tests of shard-encoded location metadata.

## Important APIs, Types, And Functions
The main type is `CheckMetadataEncodingWorkload : TestWorkload`, registered with `WorkloadFactory`. It uses `keyServersPrefix`, `keyServersEnd`, `serverKeysPrefix`, `serverKeysTrue`, `serverKeysFalse`, `serverKeysTrueEmptyRange`, `BinaryReader`, protocol-version feature detection via `hasShardEncodeLocationMetaData`, and transaction options `READ_SYSTEM_KEYS` and `READ_LOCK_AWARE`.

## Control Flow
Client 0 runs `_start`. It scans all `keyServers` metadata in batches of 1000 and classifies entries as old if values are empty or if the encoded value's protocol version lacks shard-encode support; otherwise they are new. It then scans `serverKeys` entries and classifies known boolean/empty-range values as old and everything else as new. Finally it emits counts and checks them against `shardEncodeExpected` and `allowMixedFormats`.

## State And Persistence
The workload is read-only except for trace output. It observes system metadata state in `keyServers` and `serverKeys`, retrying reads on transaction errors. `setup` can emit an error if `requireKnobFalse` was requested but the server knob is still true.

## Dependencies And Integration Points
This workload depends on FDB system key layout, protocol-version-aware serialization, the shard encoding knob, and rollback scenarios where old and new metadata can intentionally coexist. It integrates with simulation/configuration tests that toggle the feature knob.

## Risks
The serverKeys classification treats any non-legacy sentinel value as new format, so future old-format sentinel additions would need updates. The keyServers check only requires at least one new-format entry when enabled, acknowledging partial migration. In rollback mode, `allowMixedFormats` suppresses errors for leftover new entries; without it, migration residue will fail the test.

## Test Signals
Primary traces are `CheckMetadataEncodingKnobNotFalse`, `CheckMetadataEncodingResult`, and `CheckMetadataEncodingFailed`. The workload returns true from `check`, so error-severity traces and assertions are the test evidence.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/CheckMetadataEncoding.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClearSingleRange.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ClearSingleRange.cpp

## Purpose
`ClearSingleRange.cpp` defines the `ClearSingleRange` tester workload. It waits for a configured delay, then clears one configured key range in a single transaction.

## Important APIs, Types, And Functions
The file defines `ClearSingleRange : TestWorkload` and registers it with `WorkloadFactory<ClearSingleRange>`. The central actor is `fdbClientClearRange(Database db)`, which uses `Transaction`, `FDBTransactionOptions::NEXT_WRITE_NO_WRITE_CONFLICT_RANGE`, `tr.clear(KeyRangeRef(begin, end))`, `tr.commit`, and `tr.onError`.

## Control Flow
The constructor reads `begin`, `end`, and `beginClearRange` options, defaulting to `normalKeys`. Only client 0 runs `start`. The actor logs the target range, sets the next-write-no-conflict-range option, waits `startDelay`, clears the range, and commits.

## State And Persistence
The persistent effect is removal of all keys in `[begin, end)`. The transaction option prevents adding a write conflict range for the clear, which changes conflict behavior compared with a normal range clear. There is no workload-local persistence.

## Dependencies And Integration Points
The workload depends on native API transactions and tester workload registration. It includes `BulkSetup.h` but does not use any symbols from it. It can be combined with other workloads to test behavior under asynchronous range deletion.

## Risks
The retry logic is incomplete: after catching an error, the actor logs `ClearRangeError` and calls `tr.onError(err)` once, but does not loop back to reissue the clear. If the commit fails transiently, the workload may end without clearing the range. It also logs an error object even when no error was caught, which may be noisy or invalid depending on `Error` default semantics.

## Test Signals
Signals are `ClearSingleRange` and `ClearRangeError` traces. `check` always returns true, so verifying the range was actually cleared requires another workload or direct key inspection.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClearSingleRange.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClientMetric.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ClientMetric.cpp

## Purpose
`ClientMetric.cpp` defines `ClientMetric`, a workload that verifies client latency metric entries are generated and advance over time. It can set global client profiling parameters, write random keys to trigger metrics, read the client latency special/system key range, and assert that the latest versionstamp increases after additional writes.

## Important APIs, Types, And Functions
The workload uses `GlobalConfig::prefixedKey`, `fdbClientInfoTxnSampleRate`, `fdbClientInfoTxnSizeLimit`, `runRYWTransaction`, `Tuple`, `ReadYourWritesTransaction`, `Transaction`, and system-key transaction options. Helpers include `getVersionStamp`, `changeProfilingParameters`, `latencyRangeQuery`, `writeRandomKeys`, `writeKeysAndGetLatencyVersion`, and `runner`.

## Control Flow
If `toSet` is true, client 0 writes sampling probability and transaction info size limit in `setup`. `start` on client 0 runs `runner` with a timeout. `runner` writes an initial batch of random keys, waits/queries for the newest client latency entry, parses its versionstamp, writes another batch, and asserts the second newest versionstamp is larger. `latencyRangeQuery` waits for `CSI_STATUS_DELAY`, reads the global config cached values for diagnostic output, and repeatedly scans the latency range until at least one entry is present.

## State And Persistence
The workload persists random user keys, global configuration values for client profiling when enabled, and observes generated client latency info under `\xff\x02/fdbClientInfo/client_latency/...`. It does not delete the random keys or latency entries.

## Dependencies And Integration Points
It depends on the client status info pipeline, global configuration propagation, system key access, versionstamp key layout, and transaction sampling. The versionstamp offsets are derived from a sample key string and must match the client latency key format.

## Risks
The workload can wait indefinitely in `latencyRangeQuery` until the outer timeout fires if metrics are not produced, for example when sampling probability is too low or profiling is disabled. The `writeRandomKeys` loop checks `cnt >= total` before incrementing, causing one extra write relative to the intuitive total. `runner` catches errors and only logs them, so some failures may not affect `check`, which always returns true.

## Test Signals
Trace/output signals include `WaitingForLatencyMetricToBePresent`, `WriteKeysAndGetLatencyVersionFailed`, `ClientMetricErrorWhenWriteKeys`, and `ClientMetricError`. The strongest assertion is `vs2 > vs1`, indicating newer latency metrics were added.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClientMetric.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClientTransactionProfileCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ClientTransactionProfileCorrectness.cpp

## Purpose
`ClientTransactionProfileCorrectness.cpp` defines a workload that validates serialized transaction profiling entries stored in client latency info. It disables sampling before check, reads all flushed profiling chunks, reconstructs multi-chunk transaction entries, and parses protocol-version-specific event payloads to verify format sanity.

## Important APIs, Types, And Functions
The file defines parser functions for `FdbClientLogEvents` event variants, `ClientLogEventsParser::ParserBase`, `Parser_V1`, `Parser_V2`, `Parser_V3`, and `ParserFactory`. Top-level helpers include `checkTxInfoEntryFormat`, `getNumChunks`, `getChunkNum`, `getTrId`, `checkTxInfoEntriesFormat`, `changeProfilingParameters`, and `_check`. It uses `GlobalConfig`, `Tuple`, `BinaryReader`, `BinaryWriter`, and system key transaction options.

## Control Flow
Client 0 sets `csi_status_delay` and writes profiling sample rate/size limit in `setup`. `check` on client 0 first sets sample rate to zero, waits for `CSI_STATUS_DELAY`, reads the client latency counter, scans all `client_latency` entries in batches, computes total stored byte size, and calls `checkTxInfoEntriesFormat`. Single-chunk entries are parsed directly; multi-chunk entries are grouped by transaction id, concatenated in chunk order, and parsed when the final chunk arrives. Missing or out-of-order chunks are logged and discarded.

## State And Persistence
The workload changes global profiling configuration and reads persistent client latency info/counter keys under `fdbClientInfoPrefixRange`. It does not clear profiling entries. Chunk assembly is in-memory during the check.

## Dependencies And Integration Points
It depends on the exact client latency key layout, event serialization protocol versions, global config writes, client status flush timing, and `CLIENT_KNOBS` limits for value sizes, key sizes, transaction sizes, and status delay.

## Risks
Hard-coded protocol version thresholds and parser mappings must be maintained when event wire formats evolve. The counter/content-size consistency check is present but commented out, so size accounting regressions may not fail this workload. Multi-chunk entries can be legitimately missed during deletion/flush races; the workload tolerates and discards incomplete entries, which prevents false failures but can hide coverage gaps.

## Test Signals
Traces include `ClientTransactionProfilingSetup`, `ClientTransactionProfilingUnknownEvent`, `ClientTransactionProfilingSomeChunksMissing`, `ClientTransactionProfilingChunksMissing`, `ClientTransactionProfilingCtrval`, and `ClientTransactionProfilingContentsSize`. `check` returns false only if parsing encounters an unknown event or invalid entry format.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClientTransactionProfileCorrectness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClientWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ClientWorkload.cpp

## Purpose
`ClientWorkload.cpp` implements the `ClientWorkload` wrapper, which runs another `TestWorkload` inside a separate simulated client process. It lets tester workloads exercise behavior from distinct process/network/locality contexts while preserving the parent tester interface.

## Important APIs, Types, And Functions
Main helper types are `WorkloadProcessState` and `WorkloadProcess`. Public methods implemented for `ClientWorkload` include the constructor/destructor, `description`, `initialized`, `setup`, `start`, `check`, `getMetrics`, and `getCheckTimeout`. Internals use `g_simulator->newProcess`, `destroyProcess`, `onProcess`, `FlowTransport::createInstance`, `FlowTransport::transport().bind`, `Sim2FileSystem::newFileSystem`, and `Database::createDatabase`.

## Control Flow
`WorkloadProcessState::instance` creates one persistent child process per client id, choosing IPv4 or IPv6 addresses derived from the client id, assigning tester process class/locality, creating a data folder, and binding transport in the child process. `WorkloadProcess` waits for child process initialization, switches to the child process, creates the child workload and database, then switches back. `runActor` switches into the child process to run a child workload actor and switches back to the parent with the result.

## State And Persistence
State includes the simulator child process, child address/name, child data folder, child database handle, child workload reference, and static vector of per-client `WorkloadProcessState*`. The destructor schedules child-process destruction through `impl->destroy`.

## Dependencies And Integration Points
This file integrates deeply with the simulator, process-local Flow transport, simulated filesystem setup, API version selection, workload factories declared in `tester/workloads.h`, and parent/child process switching semantics.

## Risks
Future cancellation must destroy child futures on the child process; `cancelChild` exists for this cross-process lifetime hazard. `ClientWorkload::~ClientWorkload` calls `impl->destroy()` without awaiting its future, relying on actor scheduling to perform cleanup. Static process state is never removed from the vector, so lifecycle is effectively per-client for the simulation. Incorrect process switching before creating/destroying futures can lead to simulator ownership bugs.

## Test Signals
Trace events include `StartingClientWorkloadProcess`, `ClientWorkloadProcessInitialized`, `ClientWorkloadOpenDatabase`, `StartingClientWorkload`, `DeleteWorkloadProcess`, `ShutdownClientForWorkload`, and `DestroyClientWorkload`. Good tests run child workload setup/start/check/metrics and verify no process-context assertions or leaked child actors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClientWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClogRemoteTLog.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ClogRemoteTLog.cpp

## Purpose
`ClogRemoteTLog.cpp` defines `ClogRemoteTLog`, a simulation-only gray-failure workload for remote log topologies. It degrades connectivity between a selected remote TLog and most server processes, observes storage-server data lag and log exclusion, and verifies status JSON exposes gray-failure information when exclusion occurs.

## Important APIs, Types, And Functions
Key elements are `TestState`, `StatePath`, `measureMaxSSLag`, `statusError`, `statusIncomplete`, `grayFailureStatusCheck`, `getRemoteSSIPs`, `getRemoteTLogs`, `clogRemoteTLog`, `remoteTLogNotInDbInfo`, and `workload`. It uses `StatusClient::statusFetcher`, `NativeAPI::getServerListAndProcessClasses`, `ServerDBInfo`, `logSystemConfig.tLogs`, and simulator `clogPair`.

## Control Flow
Only client 0 in simulation runs. `workload` starts `clogRemoteTLog`, records `TEST_INIT`, then periodically measures max storage-server lag. `clogRemoteTLog` waits for full recovery, selects an isolated remote TLog if possible, finds remote storage-server IPs, and clogs that remote TLog against non-tester/non-CC processes for most of the test duration. The monitor records transitions between normal/high storage lag and `CLOGGED_REMOTE_TLOG_EXCLUDED` when the selected remote TLog disappears from `dbInfo` while commits are accepted. `check` compares the actual path to allowed expected paths unless buggify or insufficient isolation disables strict checking.

## State And Persistence
No database writes are performed. State lives in simulator network clog rules, `actualStatePath`, `cloggedRemoteTLog`, and `doCheck`. Status JSON is read repeatedly but not persisted by the workload.

## Dependencies And Integration Points
The workload requires simulated multi-region/remote-log configuration, storage-server status fields with `data_lag`, cluster `gray_failure` status JSON, the simulation policy remote DC id, and accurate `ServerDBInfo` log system state.

## Risks
If no isolated remote TLog exists, the workload still clogs a random remote TLog but relaxes the final check. Status collection can be incomplete during recovery; `grayFailureStatusCheck` treats incomplete status as retryable but asserts if a complete status lacks `gray_failure`. Expected state paths are necessarily timing-sensitive because lag may recover, stay high, or be superseded by exclusion.

## Test Signals
Trace events include `SSDataLag`, `MaxSSDataLag`, `ClogRemoteTLog`, `ClogRemoteTLogMoreInfo`, `GrayFailureStatus`, `GrayFailureStatusIncomplete`, `NoGrayFailure`, `ClogRemoteTLogCheck`, and `ClogRemoteTLogCheckFailed`. The final state-path match is the primary pass/fail condition.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClogRemoteTLog.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClogSingleConnection.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ClogSingleConnection.cpp

## Purpose
`ClogSingleConnection.cpp` defines a small simulation workload that clogs communication between two random simulator processes after a randomized delay. It is a simple failure-injection workload for one pair of IPs.

## Important APIs, Types, And Functions
The main type is `ClogSingleConnectionWorkload : TestWorkload`, registered by `WorkloadFactory`. It uses `g_simulator->getAllProcesses`, `g_simulator->clogPair`, `delay`, and workload options `minDelay`, `maxDelay`, and `clogDuration`.

## Control Flow
The constructor picks `delaySeconds` uniformly between `minDelay` and `maxDelay` and optionally reads `clogDuration`; if absent, a long default duration of 10000 seconds is used. `start` runs only in simulation on client 0 and maps the delay completion to `clogRandomPair`. That function picks two random processes and clogs their IP pair if they are on different IPs.

## State And Persistence
The only state is simulator network clog state. No database data or system keys are read or written.

## Dependencies And Integration Points
It depends on simulator process metadata and the tester workload framework. It can be combined with other workloads to inject random one-link degradation.

## Risks
Randomly selected processes may include tester or non-server roles; the file does not filter process classes. If both random choices share an IP, no clog is applied. The clog is one directional or pair-level according to simulator `clogPair` semantics and is not explicitly unclogged by this workload.

## Test Signals
There are no explicit trace events in `clogRandomPair`. The observable signal is simulator network behavior and downstream workload/recovery traces. `check` always returns true.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClogSingleConnection.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClogTlog.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ClogTlog.cpp

## Purpose
`ClogTlog.cpp` defines `ClogTlog`, a simulation gray-failure/recovery workload. It partitions or heavily clogs one primary TLog from all non-CC server processes, waits for recovery to leave `FULLY_RECOVERED`, and either relies on gray failure or force-excludes the bad TLog if recovery stalls.

## Important APIs, Types, And Functions
The workload uses `ServerDBInfo`, `RecoveryState`, `ManagementAPI::changeConfig`, simulator `clogPair`, `disconnectPair`, `unclogPair`, and `reconnectPair`. Core methods are `clogTlog`, `unclogAll`, `excludeFailedLog`, and `clogClient`.

## Control Flow
Client 0 in simulation runs under a timeout. `clogClient` may choose true disconnection instead of clogging, waits for other workloads to issue transactions and for full recovery, then calls `clogTlog` until near test end. `clogTlog` selects a primary local TLog not on the cluster controller IP and clogs/disconnects it in both directions with all other non-tester IPs except CC. Once recovery starts, `clogClient` either lets gray failure recover the cluster or starts `excludeFailedLog`, which force-excludes the TLog after 30 seconds without recovery progress. The actor succeeds when `dbInfo` returns to `FULLY_RECOVERED`, then unclogs all recorded pairs.

## State And Persistence
Persistent cluster state may include a forced `exclude=IP:PORT` configuration change. Runtime state includes the selected TLog, clog/disconnect pairs, `useDisconnection`, and simulator network rules.

## Dependencies And Integration Points
The workload depends on primary TLog recruitment state, cluster controller reachability, management API exclusion, simulator networking, and recovery state transitions. It is explicitly targeted at a recovery bug where a partitioned TLog could be rerecruited and stall initialization.

## Risks
The selected `tlog` is the first eligible TLog discovered and is not randomized among all eligible logs. When `useGrayFailureToRecover` is true, `excludeFailedLog` is disabled and the test relies entirely on gray failure before timeout. Failure reporting is trace-based because `check` returns true; timeout logs `ClogTLogFailure` but does not return false directly.

## Test Signals
Trace events include `ClogTlog`, `ClogTLogUseGrayFailreToRecover`, `ExcludeFailedLog`, `ClogDoneFullyRecovered`, and `ClogTLogFailure`. Recovery-state transitions and absence of stuck recovery are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ClogTlog.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/CommitBugCheck.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/CommitBugCheck.cpp

## Purpose
`CommitBugCheck.cpp` defines `CommitBug`, a regression workload for two commit-related bugs. It repeatedly verifies that sequential commits preserve final value semantics and that retry behavior around conflicts, `transaction_too_old`, and unknown commit-style errors does not produce skipped or duplicated counter values.

## Important APIs, Types, And Functions
The main type is `CommitBugWorkload : TestWorkload`, registered as `CommitBug`. It exposes actors `bug1` and `bug2`, uses `Transaction`, `tr.set`, `tr.get`, `tr.clear`, `tr.commit`, `tr.reset`, `tr.onError`, and checks error codes such as `commit_unknown_result`, `not_committed`, and `transaction_too_old`.

## Control Flow
`start` runs `bug1(cx, this) && bug2(cx, this)` under a 60-second timeout. `bug1` loops forever writing `Value1`, then `Value2`, then reading the key to ensure `Value2` is present, then clearing it. `bug2` iterates 1000 counter increments; each iteration reads the current value, ensures it equals the expected loop index, writes `i + 1`, and commits. On non-conflict/non-too-old errors, it resets and retries just the set/commit path.

## State And Persistence
Each client uses keys `B1Key<clientId>` and `B2Key<clientId>`. `bug1` clears its key every loop. `bug2` leaves the final counter value after completion. Workload state is the boolean `success`.

## Dependencies And Integration Points
The workload depends on FDB transaction retry semantics and tester parallel actor composition. It is designed to run under simulation faults that produce ambiguous commit results and conflicts.

## Risks
The `start` timeout returns `Void` even if the actors are still looping, so success depends on `success` being flipped on detected failure before check. `bug2` treats errors other than `not_committed` and `transaction_too_old` by retrying the write after reset without re-reading, which is intentional for the regression but relies on idempotence of setting the expected next value. Trace-only `CODE_PROBE`s mark expected rare error paths.

## Test Signals
Failure traces are `CommitBugFailed` and `CommitBug2Failed`; retry diagnostics include `CommitBugSetVal1Error`, `CommitBugSetVal2Error`, `CommitBugGetValError`, `CommitBugClearValError`, and `CommitBug2Error`. `check` returns `success`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/CommitBugCheck.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ConfigureDatabase.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ConfigureDatabase.cpp

## Purpose
`ConfigureDatabase.cpp` defines `ConfigureDatabase`, a randomized configuration-change workload. It changes redundancy, regions, roles, coordinators, storage engine, log engine/version/spill options, backup worker configuration, and storage migration settings, then optionally waits for storage servers to converge to the configured store type.

## Important APIs, Types, And Functions
Top-level helpers include `generateRegions`, `IssueConfigurationChange`, `valueToUInt64`, `getDatabaseName`, `issueAggressiveMigrationIfNeeded`, `randomRoleNumber`, and `singleDB`. Constants define candidate storage migration strings, log strings, redundancy modes, and backup-worker modes. The workload uses `ManagementAPI::changeConfig`, `changeQuorum`, `autoQuorumChange`, `nameQuorumChange`, `getDatabaseConfiguration`, `getStorageServers`, `ParsePerpetualStorageWiggleLocality`, and storage server `getKeyValueStoreType`.

## Control Flow
`setup` first forces `"single storage_migration_type=aggressive"`. `start` records current configuration, excludes sharded RocksDB when shard-encoded metadata is off, and client 0 runs `singleDB` until timeout. `singleDB` loops through randomized choices: wait/read recovery, delay, issue redundancy/region/role config, change quorum/name, change storage engine, change log settings, change backup worker setting, or change storage migration/perpetual wiggle settings. `check` optionally loops until storage servers report the configured store type or triggers aggressive migration if topology cannot support gradual wiggle.

## State And Persistence
Persistent state is cluster configuration and coordinator/quorum descriptor state. Storage migration settings can cause actual storage-engine migration and perpetual wiggle behavior. Metrics persist only in the workload's `retries` counter, though the loop does not visibly increment it in this file.

## Dependencies And Integration Points
The workload depends on management API configuration parsing, simulation policy datacenter topology, satellite/remote redundancy options, process locality, storage migration support, and storage server interfaces. It disables `Attrition` because random process failures can make configuration convergence checks unstable.

## Risks
Randomly generated config strings can be invalid by design, so callers must tolerate management errors from impossible configurations. The workload factory variable is named `DestroyDatabaseWorkloadFactory` even though it registers `ConfigureDatabaseWorkload`, which is confusing but legal. Storage engine exclusion depends on option values and shard encoding state. The storage convergence loop can run for a long time when migration is slow or topology cannot provide replacement teams; aggressive migration is a mitigation for small DCs.

## Test Signals
Trace events include `ConfigureDatabase_Config`, `ConfigureDatabase_WrongStoreType`, `ConfigureTestSettingWiggleLocality`, and printed `Issuing configuration change:` lines. Metrics expose `Retries`, but most correctness signals are management errors, storage-type convergence, and later `ConsistencyCheck` workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ConfigureDatabase.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ConflictRange.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ConflictRange.cpp

## Purpose
`ConflictRange.cpp` defines `ConflictRange`, a workload that stress-tests range read conflict behavior, key selectors, limits, reverse reads, and read-your-writes interactions. It compares whether a transaction that conflicts with a range read produces changed results, and whether a non-conflicting transaction preserves the original range result.

## Important APIs, Types, And Functions
The main type is `ConflictRangeWorkload : TestWorkload`, with actor `conflictRangeClient`. It uses `Transaction`, `ReadYourWritesTransaction`, `KeySelectorRef`, `getRange`, `setVersion`, `not_committed`, `timeKeeperSetDisable`, and metrics `withConflicts`, `withoutConflicts`, and `retries`.

## Control Flow
Client 0 disables the timekeeper in simulation, repeatedly initializes a numeric keyspace with random present keys plus a sentinel, generates a non-empty random range read, optionally performs a read-your-writes clear/set setup, creates transactions at the same read version, mutates random existing or absent keys in one transaction, commits it, then performs the generated range read and commit in the other transaction. If it gets `not_committed`, it re-reads and expects changed results except for documented selector/limit/sentinel edge cases. If it commits, it expects the new result to match the original result.

## State And Persistence
Persistent state is the test keyspace of zero-padded numeric keys and a sentinel just past the range. Each iteration clears/reinitializes the range and commits random mutations. Runtime state tracks inserted and cleared integer sets plus original range results.

## Dependencies And Integration Points
The workload depends on FDB conflict range semantics, key selector resolution, read-your-writes transaction behavior, and simulation timekeeper controls. It disables `RandomRangeLock` because range-lock transactions create unrelated conflicts.

## Risks
The constructor appears to read `maxOperationsPerTransaction` using the `"minOperationsPerTransaction"` option name, so the max option cannot be independently configured as written. Several expected-conflict edge cases deliberately throw `not_committed` to discard ambiguous cases where results do not change. The test assumes the keyspace remains outside system keys using the sentinel check.

## Test Signals
Metrics count `WithConflicts`, `withoutConflicts`, and `Retries`. Failure traces are `ConflictRangeError` and `ConflictRangeDump`, with detailed selector parameters and original/current results. A healthy run continually alternates conflict and non-conflict cases without SevError traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ConflictRange.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ConsistencyCheck.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ConsistencyCheck.cpp

## Purpose
`ConsistencyCheck.cpp` defines `ConsistencyCheck`, FoundationDB's broad cluster invariant workload. It can quiesce the database, suspend/resume based on a system key, validate storage/server metadata and role placement, check worker/coordinator lists, ensure consistency scan is stopped, and compare shard data across storage servers and TSS pairs.

## Important APIs, Types, And Functions
The main type is `ConsistencyCheckWorkload : TestWorkload`. Important helpers include `monitorConsistencyCheckSettings`, `runCheck`, `checkForUndesirableServers`, `checkStorageMetadata`, `checkForStorage`, `checkForExtraDataStores`, `checkWorkerList`, `checkCoordinators`, `checkUsingDesiredClasses`, `checkConsistencyScan`, `checkSingleSingleton`, and `checkSingleSingletons`. It also calls external helpers such as `quietDatabase`, `getDataDistributionQueueSize`, `getTeamCollectionValid`, `getTLogQueueInfo`, `getMaxStorageServerQueueSize`, `getKeyServers`, `getKeyLocations`, and `checkDataConsistency`.

## Control Flow
`setup` optionally quiets the database for quiescent checks and starts a monitor that watches `fdbShouldConsistencyCheckBeSuspended`. `_start` waits while suspended, then races one `runCheck` against suspension changes, repeating if `indefinite` is true. `runCheck` reads configuration and optional TSS mapping, performs quiescent-only queue/storage/worker/coordinator/role checks on the first client, then reads key server and key location metadata and calls `checkDataConsistency` across clients according to `distributed`, `shardSampleFactor`, `shuffleShards`, and rate-limit settings.

## State And Persistence
The workload mostly reads system state. It may write simulation state by disabling the timekeeper and setting `fdbSimulationPolicyState().quiesced`, and `checkForExtraDataStores` can reboot or kill simulated processes that have unexpected data stores. It maintains `success`, `repetitions`, `bytesReadInPreviousRound`, and the suspension `AsyncVar`.

## Dependencies And Integration Points
This file integrates with server DB info, data distributor, quiet database utilities, consistency scan config, TSS mapping utilities, storage server interfaces, coordinator connection strings, simulator process lists, process classes, and Flow `ProcessEvents` timeout reporting.

## Risks
The workload covers many moving cluster invariants and therefore contains numerous timing exceptions for recoveries, missing attributes, TSS recruitment, excluded processes, and region failover. In non-quiescent mode many deep checks are skipped. Some severe conditions call `testFailure` while other checks use `ASSERT`, so failure mode varies by invariant. The extra-data-store check can kill/reboot simulated processes, which is useful cleanup but can perturb concurrent workloads.

## Test Signals
Key traces include `ConsistencyCheckFailure`, `TestFailure`, `ConsistencyCheck_QuietDatabaseError`, `ConsistencyCheck_NonZeroDataDistributionQueue`, `ConsistencyCheck_TooManyTeams`, `ConsistencyCheck_NonZeroTLogQueue`, `ConsistencyCheck_WrongKeyValueStoreType`, `ConsistencyCheck_NoStorage`, `ConsistencyCheck_ExtraDataStore`, `ConsistencyCheck_WorkerMissingFromList`, `ConsistencyCheck_BadCoordinator`, role fitness traces such as `ConsistencyCheck_MasterNotBest`, and `ConsistencyCheck_FinishedCheck`. `check` returns the accumulated `success` flag.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ConsistencyCheck.cpp -->

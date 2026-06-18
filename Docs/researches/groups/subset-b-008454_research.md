# subset-b-008454 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/SimulatedCluster.cpp -->
# sources/storage-engines/foundationdb/fdbserver/SimulatedCluster.cpp

## Purpose
`SimulatedCluster.cpp` is the main simulation harness for constructing, rebooting, and destroying an in-process FoundationDB cluster used by simulation tests. It reads workload configuration files, chooses database and process topology, creates simulated machines and processes, starts `fdbd`, backup agents, DR agents, and optional simulated HTTP servers, then runs the test workload against a generated cluster file. It also supports restart tests by reconstructing machines from `restartInfo.ini` and by preserving or mutating cluster topology details such as zone IDs, coordinators, protocol versions, hostnames, SSL mode, extra databases, and process classes.

## Important APIs, Types, and Functions
The central configuration type is `TestConfig`, derived from `BasicTestConfig`. It parses legacy `.txt` INI-like files and TOML workload files. Its nested `ConfigBuilder` maps TOML configuration names to member pointers and uses variant visitors to assign ints, floats, bools, strings, vectors, optional values, `SimulationStorageEngine`, and excluded engine sets. The parser rejects unknown TOML configuration keys with `UnknownConfigurationAttribute`, records `restartInfoLocation` recursively, and converts `extraDatabaseMode` strings after parsing.

`SimulationConfig` derives from `BasicSimulationConfig` and converts `TestConfig` into a concrete database and topology configuration. Its helper methods choose storage engines, redundancy, regions, machine count, coordinators, process density, and TSS mode. Storage engine selection flows through `chooseSimulationStorageEngine()` and `STORAGE_ENGINE_CONFIG_MAPPER`, supporting SSD, memory, memory-radixtree, Redwood, and RocksDB variants when built.

The process orchestration APIs are `simulatedFDBDRebooter()`, `simulatedMachine()`, `restartSimulatedSystem()`, `setupSimulatedSystem()`, and the exported `simulationSetupAndRun()`. `runBackup()`, `runDr()`, and `runSimHTTPServer()` are auxiliary process actors. `makeIPAddressForSim()` generates deterministic IPv4 or IPv6 addresses, `reseedRandomAtTime()` resets the deterministic RNG during long tests, and `getMaxSatelliteLogs()` inspects simulated process localities to bound satellite log counts.

## Control Flow
`simulationSetupAndRun()` wraps `simulationSetupAndRunImpl()` in `uncancellable`. The implementation reads the test config, updates global simulation policy flags, possibly injects targeted storage-server restart or delay times, computes an incompatible protocol version when requested, creates a `TestSystem` simulated process, installs a simulated filesystem and transport, then either restarts a persisted system or constructs a new one. For new systems, `setupSimulatedSystem()` builds `SimulationConfig`, generates a starting configuration string, selects SSL, IPv6, hostname usage, coordinators, extra databases, server machines, tester machines, and optional HTTP-only machines, then pushes each machine actor into `systemActors`.

Each `simulatedMachine()` creates or reloads data and coordination folders, builds per-process cluster connection records, starts one `simulatedFDBDRebooter()` per IP, and waits for all process actors to terminate. On reboot, it kills open files in the machine cache, waits until `closingFiles` drains, destroys the simulated machine, then either swaps folders with another available machine, recreates folders after data loss, or reuses the same folders. The reboot loop continues until a kill type below the process-reboot threshold is returned.

`simulatedFDBDRebooter()` repeatedly creates an `ISimulator::ProcessInfo`, switches execution to that process, installs transport and `Sim2FileSystem`, binds listeners, starts `fdbd`, backup or DR agents, or an HTTP server according to `ProcessMode`, then waits for any process future or shutdown signal. It handles late reboot-and-switch requests, IO timeout conversion checks, simulated process destruction, cluster-file rewrites after data deletion, and connection-string switching for dual-cluster tests.

After machine setup, `simulationSetupAndRunImpl()` writes a temporary `fdb.cluster`, protects coordinators for restart tests, optionally schedules RNG reseeding, then calls `runTests()`. It wraps non-long-running tests in a timeout, emits timeout events, traces missed code probes, stops the simulator, sets the global `destructed` flag, and intentionally waits forever after shutdown.

## State and Persistence Behavior
The file uses deterministic randomness heavily, so topology generation is reproducible from the simulation seed unless `reseedRandomAtTime()` is enabled. Persistent state in the simulated filesystem includes per-process data folders, coordination folders, `fdb.cluster` files, and restart metadata read from `restartInfo.ini`. Restart mode uses INI values for machine count, process count, listeners per process, desired coordinators, connection string, TSS mode, mock DNS, machine IDs, localities, process class, and IP addresses. Folder swaps are tracked by the global `availableFolders` map keyed by datacenter ID.

Simulation policy state stores cross-actor signals such as extra database connection strings, chosen regions, starting disabled configuration, desired coordinators, physical datacenters, TSS mode, restart flags, backup agent mode, DR agent mode, and whether a different-protocol process was spawned. The simulated machine code deliberately manipulates open-file state and closing-file state to model crash and reboot hazards.

## Dependencies and Integration Points
The implementation depends on the Flow actor runtime, simulator interfaces, `FlowTransport`, `Sim2FileSystem`, FDB client configuration parsing, `DatabaseConfiguration`, `BackupAgent`, tester APIs, `MonitorLeader`, `WorkerInterface`, and cluster connection record types. It integrates with code probe tracing via `CODE_PROBE` and `probe::traceMissedProbes`, with mock DNS and hostnames through `INetworkConnections`, with TLS through generated listener counts and `NetworkAddress` flags, and with server startup through the `fdbd()` actor. It also coordinates with backup and DR simulation policy by starting `FileBackupAgent` and `DatabaseBackupAgent` actors in simulated processes.

## Risks and Edge Cases
The file has high coupling to global simulator and policy state. Ordering matters in `SimulationConfig::generateNormalConfig()` because later configuration calls overwrite earlier fields. Configuration parsing is assertion-heavy, so malformed test config can crash rather than produce recoverable errors. The `describe()` specializations are explicitly marked as potential ODR risks. Reboot logic relies on open-file cleanup and a bounded wait; leaked closing files trigger an assertion. Restart compatibility constrains newer features such as separate tlog spill folders, TSS, and hostnames. Region and satellite-log generation has many random branches, so insufficient machine counts or unsupported engine exclusions can make a test invalid. A hardcoded one-second wait after `setupSimulatedSystem()` is called out by comments as a fragile boot synchronization point.

## Test Signals
This file is itself part of the simulation test infrastructure. Signals include many `TraceEvent`s (`SimulatorConfig`, `SimulatedClusterStarted`, `SimulatedMachineStart`, `SimulatedFDBDShutdown`, `TestProgress`), `CODE_PROBE`s for storage engines, SSL, IPv4/IPv6, hostnames, machine reboot cases, region modes, and missed probe tracing at shutdown. Assertions validate coordinator counts, valid storage engine values, file closure, stateless class requirements, and configuration invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/SimulatedCluster.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/UID.swift -->
# sources/storage-engines/foundationdb/fdbserver/UID.swift

## Purpose
`UID.swift` adds Swift collection compatibility for the C++/Flow `UID` type exposed through `FDBServer`. It makes `Flow.UID` conform to `Hashable` so it can be used as a dictionary key, set element, or any other Swift hash-based identity.

## Important APIs, Types, and Functions
The only public API is an extension on `Flow.UID`. `hash(into:)` feeds `first()` and `second()` into the Swift hasher. `==` returns true only when both 64-bit halves match.

## Control Flow
There is no asynchronous or branching control flow beyond the equality comparison. Hashing and equality use the same two components, which preserves Swift's requirement that equal values hash identically.

## State and Persistence Behavior
The extension stores no state and performs no persistence. It depends on `UID.first()` and `UID.second()` being stable views of the underlying UID value.

## Dependencies and Integration Points
The file imports `Flow` and `FDBServer`, then extends the Flow type from Swift. The integration point is Swift code that needs FoundationDB identifiers in standard-library hashed collections.

## Risks and Test Signals
The risk is semantic drift if the underlying UID representation changes or if `first()`/`second()` no longer represent the full identity. Unit coverage should include two identical UIDs comparing equal and hashing consistently, plus different first or second halves comparing unequal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/UID.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/BackupWorker.cpp -->
# sources/storage-engines/foundationdb/fdbserver/backupworker/BackupWorker.cpp

## Purpose
`BackupWorker.cpp` implements the classic log-router backup worker. A backup worker consumes mutation log messages for a backup tag, filters candidate mutations into configured backup key ranges, writes tagged mutation log files to backup containers, records byte counts and progress in system keys, and pops tlog data only when safe. It supports current-epoch workers and catch-up workers for older backup epochs after recovery.

## Important APIs, Types, and Functions
`VersionedMessage` wraps a `LogMessageVersion`, raw message bytes, tags, and arena ownership. `isThisMessageMutation()` skips special, transaction-system, log-protocol, span-context, and OTEL span-context messages before decoding a `MutationRef`. `isCandidateBackupMessage()` accepts normal keys, metadata version key, and allowed system backup mutations, including clear-range intersection with `systemBackupMutationMask()`.

`BackupData` is the worker state container. It tracks worker identity, tag, total tags, start and end versions, recruited and backup epochs, oldest backup epoch, known committed version, saved version, `LogSystemConsumer`, database handle, buffered messages, pause state, memory lock, active backups, triggers, counters, and logging. Its `PerBackupInfo` opens the backup container and ranges through `BackupConfig`, updates started-worker metadata for current-epoch workers, and tracks per-backup file progress.

Major actors and helpers include `shouldBackupWorkerExitEarly()`, `monitorBackupStartedKeyChanges()`, `monitorBackupProgress()`, `setBackupKeys()`, `saveProgress()`, `pullAsyncData()`, `uploadData()`, `saveMutationsToFile()`, `addMutation()`, `updateLogBytesWritten()`, `checkRemoved()`, `monitorWorkerPause()`, and the exported `backupWorker()`.

## Control Flow
`backupWorker()` constructs `BackupData`, starts displacement and failure monitors, starts progress monitoring on tag 0 for current epoch workers, starts pause monitoring, checks whether an old epoch can exit early, then starts pulling and uploading. Its main loop races DB-info changes, upload completion, and actor errors. DB-info changes rebuild a log-system consumer when backup pseudo-locality is available and update `oldestBackupEpoch`. Upload completion notifies the cluster controller with `BackupWorkerDoneRequest`.

`pullAsyncData()` waits while paused, opens or refreshes a log-router peek cursor, detects popped data, updates `minKnownCommittedVersion`, buffers peeked messages under a byte `FlowLock`, advances `pulledVersion`, trims messages beyond `endVersion`, and signals upload completion for bounded old epochs. `uploadData()` periodically finds a committed version boundary no later than `maxPopVersion()`, writes messages through `saveMutationsToFile()`, erases buffered messages, commits progress, updates `savedVersion`, and calls `pop()`.

`saveMutationsToFile()` waits for active backup containers and ranges, creates one tagged log file per active backup, builds a `KeyRangeMap` from backup ranges to file indexes, decodes and filters buffered mutations, splits clear ranges by backup-range intersection, writes records in block format via `addMutation()`, finishes files, updates per-backup `lastSavedVersion`, and atomically adds file sizes to `logBytesWritten`.

## State and Persistence Behavior
Progress is persisted under `backupProgressKeyFor(myId)` using `WorkerBackupStatus`. User-visible backup progress is stored in each `BackupConfig.latestBackupWorkerSavedVersion()` by tag 0 when all tags have reported the epoch and all workers have marked the backup started. `BackupConfig.startedBackupWorkers()` and `allWorkerStarted()` coordinate backup start acknowledgement. Log bytes are persisted through atomic adds to `BackupConfig.logBytesWritten()`.

The blob/container persistence path uses `IBackupContainer::writeTaggedLogFile(begin, end, blockSize, tagId, totalTags)`. Mutation records are big-endian `(version, subversion, messageSize, message)` entries inside blocks identified by `PARTITIONED_MLOG_VERSION`; padding uses `fileBackup::makePadding()`. Popping is deferred when older epochs still need data or during shutdown, preventing loss across recovery handoff.

## Dependencies and Integration Points
The worker integrates with `BackupAgent`, `BackupContainer`, `BackupConfig`, `BackupProgress`, `LogSystem`, `LogSystemConsumer`, `ServerDBInfo`, `WaitFailure`, `WorkerInterface`, system keys such as `backupStartedKey`, `backupPausedKey`, and `backupWorkerEnabledKey`, and trace/counter infrastructure. It is exported by `BackupWorker.h` and recruited through `BackupInterface` and `InitializeBackupRequest`.

## Risks and Edge Cases
Correctness depends on writing only complete version boundaries and on not popping tlogs before durable progress is visible. `pullAsyncData()` logs an error for missing popped data but uses `ASSERT(true)`, which does not itself fail; callers depend on later behavior and trace visibility. Memory pressure is controlled by estimated message size and a lock capacity; an assertion fires if no messages can be processed while the lock has waiters. Backup start tracking only sets latest saved versions once all workers are ready, so stuck or removed workers can delay restorable progress. Clear-range splitting must match restore expectations exactly.

## Test Signals
There are no local `TEST_CASE`s in this file. The primary signals are simulation/integration tests around backup, restore, DR, recovery, backup pause, and tlog popping. Runtime observability includes `BackupWorkerMetrics`, `BackupWorkerStart`, `BackupWorkerSave`, `BackupWorkerSavedProgress`, `BackupWorkerSetVersion`, `BackupWorkerPullMissingMutations`, and `BackupWorkerDone`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/BackupWorker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/BackupWorkerRangePartitioned.cpp -->
# sources/storage-engines/foundationdb/fdbserver/backupworker/BackupWorkerRangePartitioned.cpp

## Purpose
`BackupWorkerRangePartitioned.cpp` implements the newer range-partitioned backup worker. It consumes backup-tag tlog messages, routes mutations to backup partition files according to a `PartitionMap`, persists partition-map history for old-epoch recovery, uploads deterministic partition-list metadata to every active backup container, saves progress, and notifies the cluster controller when an epoch is complete.

## Important APIs, Types, and Functions
`RangePartitionedVersionedMessage` mirrors the classic worker message wrapper but currently has an incomplete `isCandidateBackupMessage()` that returns true for all messages. `RangePartitionedLogFileInfo` tracks an active output file's backup UID, partition ID, key range, begin version, file reference, and current block end. `BackupRangePartitionedData` stores worker identity, epoch/version state, `LogSystemConsumer`, pause flag, byte lock, buffered messages, active backup metadata, partition routing maps, and triggers.

Partition-map control is handled by `pullPartitionMapFromTLog()`, `persistPartitionMapToSS()`, `loadActivePartitionMapFromSS()`, `uploadPartitionList()`, `persistAndUploadPartitionMap()`, `setActivePartitionMap()`, and `processPartitionMap()`. Backup lifecycle and progress use `onBackupChanges()`, `shouldBackupWorkerExitEarly()`, `monitorBackupStartedKeyChanges()`, `monitorBackupRangePartitionedProgress()`, `setBackupKeys()`, `saveProgress()`, `checkRemoved()`, and `monitorWorkerPause()`. Data movement uses `pullAsyncData()`, `uploadData()`, `saveMutationsToFile()`, `writeFileHeader()`, `addMutation()`, and `updateLogBytesWritten()`. The exported actor is `backupWorkerRangePartitioned()`.

## Control Flow
`backupWorkerRangePartitioned()` starts displacement, failure, progress, pause, and log-system monitors, then processes an initial partition map before pulling data. Current-epoch workers and old-epoch workers without persisted history read the first partition map from tlog and persist/upload it. Old-epoch workers first attempt to load the active partition map from system storage at their start version. After partition setup, the worker checks whether the old epoch can exit early; otherwise it monitors active backups, pulls messages, uploads data, and notifies the master on completion.

`pullAsyncData()` opens a `peekSingle()` cursor for the worker tag, skips span-context metadata, detects partition-map messages, persists and uploads new maps immediately, buffers messages under the byte lock, updates known committed and pulled versions, and trims beyond `endVersion`. Mid-stream partition maps remain in the buffer so `uploadData()` can apply them at the correct version boundary. `uploadData()` finds a safe committed boundary, scans for buffered `PartitionMapMessage`s, flushes mutations before each map, applies the map, drops the map message, writes remaining mutations, saves progress, updates `savedVersion`, and pops when allowed.

`saveMutationsToFile()` computes active output files from `keyRangeToBackupAssignment`, opens one range-partitioned log file per `(backup UID, partition ID)`, writes a file header with `RANGE_PARTITIONED_MLOG_VERSION`, partition ID, and key range, then writes candidate messages to all matching partition files. Non-clear mutations route by key lookup; clear ranges route by intersecting assigned ranges and write the full mutation once per file. Finished file sizes are accumulated per backup and persisted to `logBytesWritten`.

## State and Persistence Behavior
Partition-map history is persisted in system keys keyed by `(backupEpoch, partitionMapVersion)` using `backupPartitionMapHistoryKeyFor()` and serialized `PartitionMap` values. `loadActivePartitionMapFromSS()` uses `lastLessOrEqual()` bounded by the epoch range to find the map active at a worker start version. Blob/container state includes partition-list JSON written through `writePartitionListFile(logFolderBaseVersion, jsonContent)` and range-partitioned log files written through `writeRangePartitionedLogFile(begin, end, logFolderBaseVersion, partitionId, blockSize)`.

Progress is persisted at `backupProgressKeyFor(myId)` using `WorkerBackupStatus`, gated by `rangeBackupWorkerEnabledKey`. Backup-level latest saved versions are updated from tag 0 once all tags in the recruited epoch have progress, but only when `backupEpoch == oldestBackupEpoch`. Popping is deferred when older epochs still need data or when shutdown is in progress.

## Dependencies and Integration Points
This file integrates with `BackupPartitionMap`, `PartitionMapMessage`, `BackupProgress`, `BackupContainer`, `BackupConfig`, `LogSystem`, `LogSystemConsumer`, `ServerDBInfo`, `WaitFailure`, and backup system keys. It is exported by `BackupWorkerRangePartitioned.h`. The bottom of the file includes unit tests for `PartitionMapMessage` serialization and a `forceLinkBackupWorkerRangePartitionedTests()` shim because production linkage is not yet wired.

## Risks and Edge Cases
The most visible risk is the TODO in `RangePartitionedVersionedMessage::isCandidateBackupMessage()`: it currently returns true, so non-mutation messages can reach mutation handling unless filtered elsewhere. The file also has TODOs around concurrent identical uploads and file-level checksums. Correctness depends on partition-map messages being persisted before future old-epoch workers need them, and applied in `uploadData()` exactly at their version boundary. `setActivePartitionMap()` asserts that the current tag exists and has partitions. Missing container futures remove backups from maps, which can affect active assignment. An empty final file is intentionally written for old epochs so restore sees a continuous range through `endVersion`.

## Test Signals
Local `TEST_CASE`s cover `PartitionMapMessage` round trip with data, empty round trip, and leading-byte detection. Runtime traces include `BWRangePartitionedWaitingForPartitionMap`, `BWRangePartitionedPMHistoryWritten`, `BWRangePartitionedReceivedMidStreamPM`, `BWRangePartitionedAppliedMidStreamPM`, `BWRangePartitionedSavedProgress`, and `BWRangePartitionedDone`. Broader coverage should include recovery with old epoch workers, repartition during upload, restore continuity, and filtering once candidate filtering is implemented.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/BackupWorkerRangePartitioned.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/backupworker/CMakeLists.txt

## Purpose
This CMake file defines the `fdbserver_backupworker` static library and its basic link and unit-test targets.

## Important APIs and Build Rules
`fdb_find_sources(FDBSERVER_BACKUPWORKER_SRCS)` discovers source files in the directory. `add_flow_target(STATIC_LIBRARY NAME fdbserver_backupworker SRCS ${FDBSERVER_BACKUPWORKER_SRCS})` creates the library. `add_fdbserver_link_test()` creates a link test against `fdbserver_backupworker`, `fdbserver_logsystem`, and `fdbserver_core`. `add_fdbserver_unit_test()` creates the `backupworker` unit-test target with the same dependencies.

## Control Flow and Integration
The library receives common fdbserver include configuration through `configure_fdbserver_common_includes()`. Public include paths expose `backupworker/include`; private include paths expose the source directory. The library links privately to `fdbserver_core` and `fdbserver_logsystem`, matching the source files' use of backup interfaces, system keys, and log consumers.

## State, Risks, and Test Signals
The file has no runtime state. Build risk is mainly source discovery: new `.cpp` files in this directory join the static library automatically, so accidental test or experimental files can affect build and link behavior. The explicit link and unit-test targets are the main build-time signals that backup worker objects, including local `TEST_CASE`s, are linked.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/include/fdbserver/backupworker/BackupWorker.h -->
# sources/storage-engines/foundationdb/fdbserver/backupworker/include/fdbserver/backupworker/BackupWorker.h

## Purpose
This header publishes the classic backup worker actor to other fdbserver components while hiding the implementation details in `BackupWorker.cpp`.

## Important APIs and Types
The header forward-declares `InitializeBackupRequest` and `ServerDBInfo`, includes `BackupInterface` and Flow primitives, and declares:

`Future<Void> backupWorker(BackupInterface bi, InitializeBackupRequest req, Reference<AsyncVar<ServerDBInfo> const> db);`

The parameters carry the worker interface endpoints, the recruitment request containing tag/version/epoch details, and a live async view of database server information.

## Control Flow and Integration
Callers start this actor when the cluster controller or master recruits a classic backup worker. The returned future represents the worker lifetime and can complete normally for an old epoch, be cancelled, or fail with non-shutdown errors.

## State, Risks, and Test Signals
The header stores no state. Its risk is ABI/API coupling: changes to the function signature require all recruitment sites to update. It also intentionally keeps request and DB-info types forward-declared, limiting include fanout. Build/link tests in the backupworker CMake target verify that the declaration and implementation stay linked.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/include/fdbserver/backupworker/BackupWorker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/include/fdbserver/backupworker/BackupWorkerRangePartitioned.h -->
# sources/storage-engines/foundationdb/fdbserver/backupworker/include/fdbserver/backupworker/BackupWorkerRangePartitioned.h

## Purpose
This header publishes the range-partitioned backup worker actor to fdbserver components.

## Important APIs and Types
It forward-declares `InitializeRangeBackupRequest` and `ServerDBInfo`, includes `BackupInterface` and Flow primitives, and declares:

`Future<Void> backupWorkerRangePartitioned(BackupInterface bi, InitializeRangeBackupRequest req, Reference<AsyncVar<ServerDBInfo> const> db);`

The request type differs from the classic worker so callers can pass range-backup-specific recruitment state, including backup tag, epochs, start/end versions, and total tag count.

## Control Flow and Integration
The actor is intended to be started by backup worker recruitment code for range-partitioned backup mode. It owns its lifetime and reports completion to the cluster interface when an epoch is done. The implementation currently includes a force-link test shim, suggesting production call sites may still be in progress.

## State, Risks, and Test Signals
The header stores no state. Signature drift can break recruitment sites. Since this actor depends on partition-map setup before pulling mutations, callers must provide a request compatible with the tlog partition-map stream. Unit/link tests in the backupworker target help ensure implementation availability.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/backupworker/include/fdbserver/backupworker/BackupWorkerRangePartitioned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/CMakeLists.txt

## Purpose
This CMake file defines the `fdbserver_clustercontroller` static library and its link and unit-test targets.

## Important APIs and Build Rules
`fdb_find_sources(FDBSERVER_CLUSTERCONTROLLER_SRCS)` discovers source files in the clustercontroller directory. `add_flow_target(STATIC_LIBRARY NAME fdbserver_clustercontroller SRCS ${FDBSERVER_CLUSTERCONTROLLER_SRCS})` creates the library. `add_fdbserver_link_test()` creates `fdbserver_clustercontrollerlinktest` against clustercontroller, logsystem, and core. `add_fdbserver_unit_test()` creates the `clustercontroller` unit-test target with the same dependencies.

## Control Flow and Integration
Common includes are configured with `configure_fdbserver_common_includes()`. The public include directory is `clustercontroller/include`; the source directory is private. The target links privately with `fdbserver_core` and `fdbserver_logsystem`, matching cluster-controller code that coordinates workers, recovery, and log-system state.

## State, Risks, and Test Signals
There is no runtime state. As with other directory-level FoundationDB CMake files, automatic source discovery can accidentally include new sources if they are placed in the directory. Link and unit-test targets provide build-time validation that clustercontroller sources and tests link against core and logsystem dependencies.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/CMakeLists.txt -->

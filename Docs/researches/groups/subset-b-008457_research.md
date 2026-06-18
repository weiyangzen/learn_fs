# Research: subset-b-008457

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterRecovery.cpp -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterRecovery.cpp

## Purpose
`ClusterRecovery.cpp` implements the cluster-controller side of FoundationDB database recovery. It recruits a new master/sequencer and transaction system roles, locks and updates coordinated state, recovers transaction state from the previous log system epoch, starts a new log epoch, writes the recovery transaction, registers the recovered master with the cluster controller, and keeps registration/coordinated-state metadata current until the next recovery. This file is the active state-machine implementation behind the contracts declared in `ClusterRecovery.h`.

## Important APIs, Types, and Functions
- `normalClusterRecoveryErrors()` and `isNormalClusterRecoveryError()` define the error set treated as expected recovery turnover, including failed proxies/resolvers/tlogs, recruitment exhaustion, coordinator conflicts, worker removal, and recovery timeout/failure paths.
- `recoveryTerminateOnConflict()` races coordinated-state conflict against state switching and throws `worker_removed` when another recovery wins before this one becomes fully recovered.
- `recruitNewMaster()` recruits the master in the cluster-controller data center, updates `masterProcessId`, increments unfinished recovery accounting, and handles forced master failure/retry behavior.
- `clusterRecruitFromConfiguration()` and `clusterRecruitRemoteFromConfiguration()` wrap cluster-controller worker selection with retry/queue behavior for primary and remote recruitment.
- `newCommitProxies()`, `newGrvProxies()`, `newResolvers()`, `newTLogServers()`, and `newSeedServers()` initialize all transaction-system roles for the new epoch.
- `trackTlogRecovery()` continuously writes evolving `DBCoreState` to coordinators while old generations are purged and new logs become fully committed.
- `changeCoordinators()`, `configurationMonitor()`, `updateRegistration()`, `sendMasterRegistration()`, and `updateLogsValue()` keep cluster metadata, master registration, and coordinator state aligned after recovery.
- `ProvisionalMaster` and `provisionalMaster()` create provisional proxy endpoints during stalled recovery so emergency configuration transactions can be accepted and merged into the eventual recovery transaction.
- `monitorInitializingTxnSystem()` enforces an exponential-backoff timeout for transaction-system initialization.
- `recruitEverything()`, `readTransactionSystemState()`, `sendInitialCommitToResolvers()`, `recoverFrom()`, and `clusterRecoveryCore()` form the primary recovery pipeline.
- `getRecoveryEventName()` centralizes recovery trace event names using a knob-controlled prefix for compatibility with tooling.

## Control Flow
The top-level flow starts in `clusterRecoveryCore()`. It begins a recovery trace interval, adds master failure monitoring, sets the recovery state to `READING_CSTATE`, and reads coordinated state through `ReusableCoordinatedState`. Protocol compatibility is checked before the code transitions to `LOCKING_CSTATE`.

Recovery then calls `recoverAndEndLogSystemEpoch()` to stop the prior log epoch and obtains changing `oldLogSystems` as recovery discovers or replaces log systems. The core state recovery count is incremented, protocol-version fields may be updated, and the new state is written back to coordinators. This early write is raced with epoch-ending work so coordinator conflicts displace the current recovery promptly.

Once an old log system is available, `recoverFrom()` reads the old transaction system state by opening a `LogSystemDiskQueueAdapter` and `IKeyValueStore` over the old log system. It computes `lastEpochEnd`, `recoveryTransactionVersion`, reads persisted configuration, tag locality mappings, server tags, history tags, version epoch, and minimum required commit version. Forced recovery narrows tags/locality to the safe locality and mutates configuration to one usable region in the local data center.

`recoverFrom()` then starts `recruitEverything()`. In parallel, after a configured delay, a `ProvisionalMaster` exposes provisional commit and GRV proxy interfaces. If normal recruitment finishes first, any generated configuration changes are merged into the pending recovery transaction. If an emergency transaction arrives first, the code validates it as a configuration-affecting transaction, applies it to `self->configuration`, resets `initialConfChanges`, re-applies forced recovery constraints when needed, and restarts recruitment if the configuration changed.

`recruitEverything()` validates configuration, recruits workers from `ClusterControllerData`, records primary/remote dc IDs, initializes seed storage servers for a brand-new database, then initializes commit proxies, GRV proxies, resolvers, and the new log epoch concurrently. Initialization is raced against `monitorInitializingTxnSystem()`, which scales timeout by unfinished recovery count. After all roles initialize, the master interface receives `UpdateRecoveryDataRequest`.

After recruitment, `clusterRecoveryCore()` asserts minimum role counts and writes the recovery transaction. For existing databases it sets `lastEpochEndKey` first, handles snapshot restore markers, pause-backup mutations, forced recovery kill/reboot/lock-owner mutations, and coordinator/log/datacenter metadata. For a new database it seeds initial shard servers as the first transaction at version 1. Configuration changes from normal recruitment or emergency transactions are appended early but after the required `lastEpochEndKey` ordering. The transaction is sent through the first commit proxy, while transaction state is broadcast to commit proxies and optionally resolvers, and resolvers receive an initial resolve batch through `sendInitialCommitToResolvers()`.

After the recovery commit and transaction-state broadcast finish, the code starts `trackTlogRecovery()`. That actor writes new log-system core state, purges old recovered generations only after durable cstate writes, sends `cstateUpdated` and `recoveryReadyForCommits`, and advances recovery state through `ALL_LOGS_RECRUITED`, `STORAGE_RECOVERED`, and `FULLY_RECOVERED`. `clusterRecoveryCore()` waits for `cstateUpdated`, records recovery duration/availability events, enters `ACCEPTING_COMMITS`, starts coordinator-change/configuration-monitor actors, starts backup/range-backup workers if configured, and then waits forever until failure or cancellation.

## State and Persistence Behavior
Recovery persists and validates multiple state layers:
- Coordinated state stores `DBCoreState`, recovery count, protocol compatibility, tlog generations, and final recovery completion. `ReusableCoordinatedState` writes through `MovableCoordinatedState::setExclusive()` and rereads non-final writes to detect conflicting masters.
- Transaction state is recovered from the old log system into `txnStateStore`, then selectively updated by applying recovery metadata mutations before the recovery commit is sent.
- Version state is derived from old log end, `MAX_VERSIONS_IN_FLIGHT`, forced recovery knobs, `versionEpochKey`, `minRequiredCommitVersionKey`, and simulation buggify paths.
- Configuration state is read from `configKeys`, modified by emergency transactions or forced recovery, serialized into the recovery transaction, and watched after recovery by `configurationMonitor()`.
- Log metadata is stored through `logsKey`, log-system core state, `tagLocalityListKeys`, `serverTagKeys`, `serverTagHistoryKeys`, `tLogDatacentersKeys`, `primaryLocalityKey`, coordinator keys, and backup version keys.
- `trackTlogRecovery()` deliberately delays in-memory old-generation purge until after durable cstate writes to avoid losing old tlog references before a future recovery can lock them.
- `discardCommit()` consumes and acknowledges the transaction-state store's pending commit message without persisting it as a real committed recovery-side write.

## Dependencies and Integration Points
This file ties together cluster-controller worker recruitment, master interfaces, transaction proxies, resolvers, tlogs, storage-server seeding, log-system epoch management, backup progress, coordinator movement, system-key encoding, and Flow actors/coroutines. Major dependencies include `ClusterControllerData`, `MasterInterface`, `WorkerInterface`, `DatabaseConfiguration`, `DBCoreState`, `LogSystem`, `LogSystemConfig`, `LogSystemDiskQueueAdapter`, `IKeyValueStore`, `BackupProgress`, `applyMetadataMutations()`, `seedShardServers()`, and Flow primitives such as `Future`, `Promise`, `AsyncVar`, `race`, `getAll`, and `TraceEvent`.

External integration is mostly via RPC endpoints: worker recruitment endpoints, proxy initialization endpoints, resolver initialize/resolve endpoints, tlog rejoin, master registration, change-coordinators request stream, and provisional proxy endpoints. Operational tooling integrates through `TraceEvent` names, `EventCacheHolder` tracking keys, recovery status codes, and counters maintained on `ClusterRecoveryData`.

## Risks and Edge Cases
- Correctness relies on strict ordering of the recovery transaction, especially placing `lastEpochEndKey` first for existing databases and preserving `COMMIT_ON_FIRST_PROXY` assumptions by storing the first commit proxy at index 0.
- Coordinated-state conflict handling is subtle: non-final writes reread state and can throw `worker_removed`, while final writes send `fullyRecovered` and stop conflict termination.
- Too many old generations can delay or stop recovery, and simulation may disable connection failures to make the condition diagnosable.
- Forced recovery mutates usable regions, kills unsafe storage locality, and writes reboot/lock-owner markers. Misuse can intentionally sacrifice unavailable regions and requires the cluster-controller dc ID.
- Provisional master emergency transactions are intentionally narrow and ignore read conflict ranges. The code prevents `usable_regions` changes after an initialized original configuration, but other configuration mutations still affect recruitment.
- Initialization timeout parameters are validated and can park forever if invalid or if unfinished recoveries exceed a configured ceiling.
- `getRecoveryEventName()` contains a duplicate `CLUSTER_RECOVERY_SS_RECRUITMENT_EVENT_NAME` insertion for `"RecoverySnapshotCheck"` after a correct snapshot insertion. Because `std::map::insert` does not overwrite, this appears harmless but is a maintenance hazard.
- Backup/range-backup recruitment depends on persisted backup progress and minimum backup version filtering. Incorrect progress interpretation can under- or over-recruit old backup work.

## Test Signals
The file is heavily instrumented for simulation and operational testing: `CODE_PROBE`, `buggify()`, `TraceEvent` recovery status transitions, debug restored-version checks, simulation-only max-generation behavior, assertions on role counts and state invariants, and normal-error classification. Useful test signals include successful transitions through `reading_coordinated_state`, `locking_coordinated_state`, `reading_transaction_system_state`, `initializing_transaction_servers`, `recovery_transaction`, `writing_coordinated_state`, `accepting_commits`, and ultimately `fully_recovered`; timeout traces from `monitorInitializingTxnSystem()`; and recovery commit traces/errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterRecovery.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterRecovery.h -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterRecovery.h

## Purpose
`ClusterRecovery.h` declares the shared data structures and public recovery functions used by the cluster controller and master recovery implementation. It defines recovery event types, coordinated-state helpers, and the `ClusterRecoveryData` state object that carries all mutable recovery context through the actor pipeline implemented in `ClusterRecovery.cpp`.

## Important APIs, Types, and Functions
- `ClusterRecoveryEventType` enumerates trace/event-cache categories for state, committed tlogs, duration, generation count, seed storage recruitment, invalid config, recovering/recovered config, snapshot checks, backup pausing, recovery commit, availability, and metrics.
- `recoveryTerminateOnConflict()` and `getRecoveryEventName()` are declared here for recovery conflict handling and trace naming.
- `ReusableCoordinatedState` wraps `MovableCoordinatedState` with recovery-specific read/write behavior, previous/current `DBCoreState`, conflict monitoring, final-write semantics, and coordinator movement.
- `ClusterRecoveryData` is a reference-counted, non-copyable aggregate carrying controller pointers, db id, versions, configuration, coordinators, log system handles, transaction-state storage, recruited role interfaces, master identity, recovery promises/triggers, counters, and event cache holders.
- `recruitNewMaster()`, `cleanupRecoveryActorCollection()`, `clusterRecoveryCore()`, and `isNormalClusterRecoveryError()` are the main exported functions for the cluster-controller recovery loop.

## Control Flow
`ReusableCoordinatedState::read()` reads raw coordinator state, deserializes `DBCoreState`, initializes `prevDBState`/`myDBState`, and registers a conflict actor via `addActor`. `write()` serializes a new `DBCoreState` with the appropriate protocol feature version, writes it exclusively, updates `myDBState`, and either rereads to verify non-final writes or sends `fullyRecovered` for final writes.

`ClusterRecoveryData` is constructed by the cluster-controller recovery actor before `clusterRecoveryCore()` runs. The constructor initializes version fields to invalid values, creates recovery triggers/promises, sets up counters and event cache holders, and starts counter tracing. It also rejects forced recovery if no cluster-controller dc ID is available.

The destructor closes `txnStateStore` if it was opened during recovery. Other cleanup is actor-driven through `cleanupRecoveryActorCollection()` in the implementation.

## State and Persistence Behavior
`ReusableCoordinatedState` is the header's main persistence-sensitive type. It protects coordinated-state writes with `finalWriteStarted` so no further writes can proceed after a final write begins. Non-final writes deliberately reset `MovableCoordinatedState`, reread, compare against the written state, and install a fresh conflict monitor. This makes cstate changes act as a recovery fencing mechanism.

`ClusterRecoveryData` stores both durable-state mirrors and transient runtime state:
- Durable mirrors: `lastEpochEnd`, `recoveryTransactionVersion`, `versionEpoch`, `liveCommittedVersion`, `minKnownCommittedVersion`, `originalConfiguration`, `configuration`, `coordinators`, `dcId_locality`, `allTags`, and `cstate`.
- Runtime handles: `logSystem`, `txnStateLogAdapter`, `txnStateStore`, recruited proxies/resolvers/backup workers, provisional proxies, and `lastCommitProxyVersionReplies`.
- Control promises: `registrationTrigger`, `recoveryReadyForCommits`, `cstateUpdated`, `addActor`, and `recruitmentStalled`.
- Observability state: counters and event cache holders for metacluster metadata, software-version compatibility, recovered config, recovery state, generations, duration, availability, and metrics.

## Dependencies and Integration Points
The header depends on core FoundationDB server types: `DatabaseContext`, replication utilities, coordinated state, coordinator interfaces, `ClusterController.h`, `DBCoreState`, knobs, key-value stores, log systems, log-system disk queues, worker interfaces, Flow coroutines, errors, and system monitoring. It ends by including `MoveKeys.h`, making move-key types available to users of the header.

`ClusterRecoveryData` integrates directly with `ClusterControllerData`, `ServerDBInfo`, `MasterInterface`, `ClusterControllerFullInterface`, `ServerCoordinators`, and transaction-system role interfaces. The public declarations are consumed by the cluster controller code that recruits masters and runs `clusterRecoveryCore()`.

## Risks and Edge Cases
- `ClusterRecoveryData` is intentionally broad and mutable. Most fields are shared across asynchronous actors, so ordering is enforced by promises, actor cancellation, and state-machine phases rather than encapsulation.
- `ReusableCoordinatedState::_write()` parks forever if a write is attempted after a final write starts, which is correct for fencing but can make misuse look like a hang.
- Serialization protocol selection depends on `SERVER_KNOBS->RECORD_RECOVER_AT_IN_CSTATE`; mixed-version or feature-removal changes require care because coordinated-state bytes must stay readable by recovery participants.
- Forced recovery safety depends on the constructor check for `clusterControllerDcId`; callers should not assume `forceRecovery` remains true after construction.
- `txnStateStore` ownership is raw-pointer based and closed in the destructor, while `txnStateLogAdapter` is stored as a raw pointer managed by the adapter/store flow; lifetime assumptions are important.

## Test Signals
Tests and simulation can assert state through recovery trace event names, `ClusterRecoveryData` counters, and cstate conflict behavior. Important observable signals include `RecoveryTerminated` with conflict or cstate-change reasons, event-cache updates for recovery state/generations/duration/availability, counter collection logs under `RecoveryMetrics`, and forced recovery rejection via `ForcedRecoveryRequiresDcID`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterRecovery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/RatekeeperMonitor.cpp -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/RatekeeperMonitor.cpp

## Purpose
`RatekeeperMonitor.cpp` implements the cluster-controller helper that detects whether ratekeeper has continuously reported a zero TPS limit long enough to justify failover behavior. It also contains a focused Flow unit test for the sustained-zero detection logic.

## Important APIs, Types, and Functions
- `RatekeeperMonitor::hasSustainedZeroRatekeeperTpsLimit(double tpsLimit, double currentTime, double zeroTpsLimitDuration)` is the only implemented production method in this file.
- The unit test `TEST_CASE("/fdbserver/clustercontroller/hasSustainedZeroRatekeeperTpsLimit")` validates first-observation, threshold, reset, restart, and disabled-duration behavior.

## Control Flow
`hasSustainedZeroRatekeeperTpsLimit()` first resets observation and returns false if the configured duration is non-positive or the current TPS limit is positive. If the limit is zero and this is the first zero observation, it stores `currentTime` and returns false. On later zero observations, it returns true only when `currentTime - zeroRatekeeperTpsLimitStartTime >= zeroTpsLimitDuration`.

The test constructs a monitor, observes a zero limit at time 100, verifies no immediate sustained result, verifies threshold behavior just before and at 5 seconds, verifies a positive TPS limit clears the start time, verifies a new zero window starts at time 107, and verifies duration `0.0` disables detection and clears state.

## State and Persistence Behavior
The implementation has no durable persistence. It mutates only the in-memory optional `zeroRatekeeperTpsLimitStartTime` field owned by `RatekeeperMonitor`. Reset happens on positive TPS limits and disabled/invalid duration. The caller controls time by passing `currentTime`; the header default uses `now()`.

## Dependencies and Integration Points
The source includes `RatekeeperMonitor.h` and `flow/UnitTest.h`. The monitor is intended for cluster-controller logic that evaluates ratekeeper health or throttling state, using `SERVER_KNOBS->CC_FAILOVER_DUE_TO_TPS_LIMIT_DURATION` by default through the header declaration.

## Risks and Edge Cases
- The function treats any `tpsLimit <= 0` as zero/sustained candidate; negative values are not distinguished from zero.
- Non-monotonic `currentTime` can delay detection because elapsed duration is computed directly from the first observation.
- A non-positive duration disables the observation and clears state, which is useful for a knob-off mode but can surprise callers expecting immediate detection.
- The monitor tracks only one continuous window and has no smoothing or tolerance for brief positive blips.

## Test Signals
The embedded Flow unit test provides direct coverage of the state machine. Additional integration tests should verify the cluster-controller failover path that consumes this monitor, especially that ratekeeper recovery to positive TPS cancels any pending failover decision.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/RatekeeperMonitor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/RatekeeperMonitor.h -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/RatekeeperMonitor.h

## Purpose
`RatekeeperMonitor.h` declares a small stateful helper used by cluster-controller code to track how long ratekeeper has advertised a zero TPS limit. The helper abstracts the duration calculation and reset behavior behind a single monitor class.

## Important APIs, Types, and Functions
- `RatekeeperMonitor::resetZeroRatekeeperTpsLimitObservation()` clears any active zero-limit observation.
- `RatekeeperMonitor::hasSustainedZeroRatekeeperTpsLimit()` evaluates whether a zero TPS limit has lasted at least the configured duration. Defaults use `now()` and `SERVER_KNOBS->CC_FAILOVER_DUE_TO_TPS_LIMIT_DURATION`.
- `RatekeeperMonitor::getZeroRatekeeperTpsLimitDuration()` returns elapsed time since the active zero observation or `0.0` when no observation is active.
- `RatekeeperMonitor::getZeroRatekeeperTpsLimitStartTime()` exposes the optional start time for tests and diagnostics.

## Control Flow
The header exposes a caller-driven polling model. Callers feed ratekeeper's current TPS limit into `hasSustainedZeroRatekeeperTpsLimit()`. Positive limits or disabled duration reset the monitor. Continuous zero-limit calls first set the start time, then later report true when the elapsed duration reaches the threshold. Consumers can separately inspect elapsed duration for status reporting.

## State and Persistence Behavior
The class stores one private field, `Optional<double> zeroRatekeeperTpsLimitStartTime`. It has no persistent storage, no actor ownership, and no concurrency control. It assumes calls are made from the owning cluster-controller context.

## Dependencies and Integration Points
The header includes `fdbserver/core/Knobs.h` for the default failover duration, `flow/Optional.h`, and `flow/flow.h` for `now()`. It forward declares `ClusterControllerData`, though this declaration is not used directly in the class. The likely integration point is cluster-controller monitoring/recruitment logic that observes ratekeeper limits and decides whether zero throughput is sustained enough to trigger failover.

## Risks and Edge Cases
- Because default arguments call global time and knob state, tests should pass explicit `currentTime` and duration when deterministic behavior is needed.
- The class is intentionally minimal and does not track ratekeeper identity. If ratekeeper is re-recruited, callers should reset or recreate the monitor to avoid carrying a zero-limit window across role instances unless that behavior is intended.
- Optional elapsed duration returns `0.0` for both no active observation and an observation whose start time equals current time; callers needing that distinction should inspect `getZeroRatekeeperTpsLimitStartTime()`.

## Test Signals
The implementation file contains a unit test for the public state transitions. Integration-level test signals should include failover not firing before the knob duration, firing at or after the duration, and clearing after positive TPS or knob disablement.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/RatekeeperMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/SingletonRoles.h -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/SingletonRoles.h

## Purpose
`SingletonRoles.h` defines lightweight wrappers for cluster-controller-managed singleton roles: ratekeeper, data distributor, and consistency scan. The wrappers provide a common shape for checking presence, publishing role interfaces into `ServerDBInfo`, halting existing singletons, and triggering recruitment. The file also defines a recruitment throttler for singleton re-recruit attempts.

## Important APIs, Types, and Functions
- `PID_USED_AMP_FOR_NON_SINGLETON` is a placement weighting constant used elsewhere to make processes already occupied by non-singleton roles less attractive for singleton placement.
- `template <class Interface> class Singleton` stores a reference to an `Optional<Interface>` and exposes `getInterface()` and `isPresent()`.
- `RatekeeperSingleton` maps to `Role::RATEKEEPER` and `ProcessClass::Ratekeeper`, writes `cc.db.setRatekeeper()`, sends `HaltRatekeeperRequest`, and triggers `cc.recruitRatekeeper`.
- `DataDistributorSingleton` maps to `Role::DATA_DISTRIBUTOR` and `ProcessClass::DataDistributor`, writes `cc.db.setDistributor()`, sends `HaltDataDistributorRequest`, and triggers `cc.recruitDistributor`.
- `ConsistencyScanSingleton` maps to `Role::CONSISTENCYSCAN` and `ProcessClass::ConsistencyScan`, writes `cc.db.setConsistencyScan()`, sends `HaltConsistencyScanRequest`, and triggers `cc.recruitConsistencyScan`.
- `SingletonRecruitThrottler::newRecruitment()` returns the wait time needed to enforce `SERVER_KNOBS->CC_THROTTLE_SINGLETON_RERECRUIT_INTERVAL` between recruitment starts and records the current start time.

## Control Flow
Cluster-controller code can instantiate the appropriate singleton wrapper around an optional interface. If present, `setInterfaceToDbInfo()` publishes it to the database info and emits a trace event. `halt()` sends the relevant halt RPC to the worker/process recorded by process ID and stores a future in `cc.id_worker[pid]` so broken promises become non-failing `Never()` futures. `recruit()` updates `cc.lastRecruitTime` and sets the role-specific recruitment trigger.

The throttler is call-based: each recruitment start calls `newRecruitment()`, receives a non-negative delay, and updates `lastRecruitStart` to the current time. The first call starts from `-1`, so the computed wait is normally zero after process uptime exceeds the configured interval.

## State and Persistence Behavior
This header has no durable persistence. The singleton wrappers mutate in-memory cluster-controller state: `ServerDBInfo` via `cc.db`, worker halt futures via `cc.id_worker`, recruitment triggers, and `lastRecruitTime`. The singleton interface reference is borrowed from a caller-owned `Optional<Interface>`, so lifetime is external. `SingletonRecruitThrottler` stores only `lastRecruitStart`.

## Dependencies and Integration Points
The header depends on `ClusterController.h`, `RatekeeperInterface.h`, and `DataDistributorInterface.h`. `ConsistencyScanInterface` is available through the included cluster-controller-related headers. Integration points include cluster-controller role tracking, process-class fitness/recruitment code, singleton halt endpoints, and `ServerDBInfo` publication consumed by clients and other server roles.

## Risks and Edge Cases
- `Singleton::getInterface()` calls `Optional::get()` without checking presence; callers must use it only after `isPresent()` or equivalent logic.
- `RatekeeperSingleton` and `DataDistributorSingleton` check both interface presence and `cc.id_worker.contains(pid)` before assigning halt futures. `ConsistencyScanSingleton::halt()` checks only interface presence before indexing `cc.id_worker[pid]`, which can create or access an entry for an absent process ID depending on map semantics; this asymmetry is worth reviewing.
- The wrappers store references to optional interfaces. They should not outlive the optional values they wrap.
- Recruitment trigger methods do not themselves throttle; callers must use `SingletonRecruitThrottler` or equivalent scheduling.
- `PID_USED_AMP_FOR_NON_SINGLETON` assumes fewer than 100 singleton roles; adding many singleton role types would require revisiting placement weighting.

## Test Signals
Useful tests would cover publishing each singleton into `ServerDBInfo`, halting only the intended worker endpoint, recruitment trigger setting, throttler wait-time calculations, and absent-interface no-op behavior. Existing trace event names `CCRK_SetInf`, `CCDD_SetInf`, and `CCCK_SetInf` provide operational evidence that singleton interfaces were published.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/SingletonRoles.h -->

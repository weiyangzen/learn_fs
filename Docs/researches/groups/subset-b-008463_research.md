# Research Group subset-b-008463

This grouped report covers FoundationDB `fdbserver` core interface/configuration headers and coroutine thread-pool implementations. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/Knobs.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/Knobs.h

## Purpose
`Knobs.h` declares `ServerKnobs`, the server-side runtime tuning surface for FoundationDB. It centralizes hundreds of typed knobs that shape version advancement, transaction logs, data distribution, storage engines, recovery, ratekeeper limits, worker health, coordination, tracing, encryption, Redwood/RocksDB behavior, simulation probabilities, and feature flags.

## Important APIs, Types, And Functions
The key type is `ServerKnobs : KnobsImpl<ServerKnobs>`, constructed and initialized with `Randomize`, `ClientKnobs*`, and `IsSimulated`. Public lifecycle helpers are `resetServerKnobs`, `initializeServerKnobs`, `setupServerKnobs`, `tryParseServerKnobValue`, `parseServerKnobValue`, `trySetServerKnob`, and `setServerKnob`. `SERVER_KNOBS` is the global singleton pointer and `getServerKnobs()` returns a reference.

## Control Flow
This header is declarative; initialization and parsing are implemented elsewhere. Runtime code reads fields directly from `SERVER_KNOBS`, while setup code parses knob overrides and simulation randomization before roles start.

## State And Persistence Behavior
Knobs are process memory state, not durable database state. They indirectly affect persistent behavior by changing log retention, MVCC windows, storage engine options, checkpoint settings, compaction, movement throttles, and recovery timing. Unsafe or randomized knobs can change simulation determinism and operational safety.

## Dependencies And Integration Points
It depends on `KnobValue`, `flow/Knobs.h`, Swift support, RPC locality, and client knobs. Nearly every server subsystem integrates through this file: TLogs, commit proxies, resolvers, DD, ratekeeper, storage servers, cluster controller, workers, coordination, and storage engines.

## Risks And Edge Cases
The risk is configuration coupling: changing a knob type, name, default, or unit can silently alter consensus, recovery, rate limiting, or storage behavior. Several comments mark experimental or dangerous settings, such as storage-server reboot on I/O timeout, RocksDB nondeterminism, sharded RocksDB experiments, and physical-shard movement.

## Test Signals
Tests typically observe this file indirectly through simulation suites and role-specific tests. Good signals are explicit knob override parsing, deterministic randomized values in simulation, feature-gated behavior, storage engine option propagation, and workload/recovery tests passing under randomized knobs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/Knobs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LatencyBandConfig.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LatencyBandConfig.h

## Purpose
This header defines the serialized configuration for latency-band telemetry. It lets the system parse JSON configuration into request-specific latency buckets and optional request-size limits for GRV, read, and commit paths.

## Important APIs, Types, And Functions
`LatencyBandConfig` contains `GrvConfig`, `ReadConfig`, and `CommitConfig`. `RequestConfig` stores `std::set<double> bands`, implements JSON loading through `fromJson`, and supports equality via virtual `isEqual`. `ReadConfig` adds `maxReadBytes` and `maxKeySelectorOffset`; `CommitConfig` adds `maxCommitBytes`. `LatencyBandConfig::parse(ValueRef)` is the public parser.

## Control Flow
The parser consumes a configuration string, builds per-request subconfigs from JSON, and later serializes the result through `ServerDBInfo`. Equality checks delegate to subtype-specific fields so broadcasts can detect material changes.

## State And Persistence Behavior
The config is transient cluster metadata carried in `ServerDBInfo`; it is not persisted by this header. Serialization preserves bands and optional thresholds for cross-process propagation.

## Dependencies And Integration Points
It depends on FDB types and `JSONDoc`. `ServerDBInfo` includes `Optional<LatencyBandConfig>`, making it visible to workers and request-serving roles that emit latency metrics.

## Risks And Edge Cases
Invalid JSON, missing fields, negative/empty bands, and equality between base/subtype configs are the main risks. Optional thresholds must remain absent when unspecified so defaults are not confused with explicit zero limits.

## Test Signals
Useful tests parse representative JSON strings, round-trip serialization, compare equal and unequal configs, and confirm read/commit thresholds are applied only to their matching request classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LatencyBandConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LeaderElection.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LeaderElection.h

## Purpose
`LeaderElection.h` declares the coordinator-backed sticky leader election API used by cluster controllers and other leader-like server components.

## Important APIs, Types, And Functions
The template `tryBecomeLeader` accepts `ServerCoordinators`, a proposed local leader interface, an `AsyncVar<Optional<LeaderInterface>>` for the best known leader, connection state, and priority info. `tryBecomeLeaderInternal` handles serialized values. `changeLeaderCoordinators` forwards coordinator replacement information.

## Control Flow
The template serializes the proposed interface with `ObjectWriter::toValue(..., IncludeVersion())`, starts the internal election actor, and races/combines it with `asyncDeserialize` to keep the typed `outKnownLeader` updated. If the local proposal becomes leader, the known leader reflects that interface until displaced or cancelled.

## State And Persistence Behavior
Leader state is stored through the coordination service, not this header. The local output is transient `AsyncVar` state. Serialization versioning matters because coordinator values can outlive a process.

## Dependencies And Integration Points
It depends on `fdbrpc`, locality, FDB types, `ServerCoordinators`, `ClusterControllerPriorityInfo`, object serialization, and async deserialization. It integrates with cluster-controller candidacy and coordinator change workflows.

## Risks And Edge Cases
The main risks are stale serialized leader interfaces, cancellation semantics, priority/fitness races, and cross-version compatibility of leader interface serialization. Sticky leadership can mask degraded leaders until communication failures are detected.

## Test Signals
Simulation tests should show one active leader, stable leadership through benign coordinator polling, displacement when a better/new leader wins, correct cancellation cleanup, and correct behavior after coordinator connection string changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LeaderElection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LogProtocolMessage.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LogProtocolMessage.h

## Purpose
This file defines a reserved transaction-log message that announces the protocol version used to deserialize subsequent mutation messages on a storage-server tag stream.

## Important APIs, Types, And Functions
`LogProtocolMessage` serializes a leading `MutationRef::Reserved_For_LogProtocolMessage` byte followed by `IncludeVersion()`. Helpers include `toString`, `startsLogProtocolMessage`, `isNextIn`, and the `applyVersionStartingHere` read/write overloads.

## Control Flow
Commit/log code injects this message into the same stream as mutations. Consumers peek one byte to distinguish it from normal `MutationRef` data, then apply the embedded protocol version before decoding later messages.

## State And Persistence Behavior
The message is persisted in the TLog stream like other log messages and affects in-memory decoding state for the reader. It carries no payload beyond version metadata.

## Dependencies And Integration Points
It depends on `FDBTypes`, `CommitTransaction`, mutation type reservations, and Flow serialization. It integrates with TLog peeking, storage-server recovery, and any future mutation serialization migration.

## Risks And Edge Cases
The leading byte must remain permanently reserved or storage servers could misclassify mutations. The comment notes this mechanism has not been exercised by an actual mutation format change, so compatibility testing is critical before relying on it.

## Test Signals
Tests should verify byte discrimination, serialization round trips across protocol versions, mixed streams of protocol messages and mutations, and recovery from logs containing the marker.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LogProtocolMessage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LogSystemConfig.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LogSystemConfig.h

## Purpose
`LogSystemConfig.h` models the active and historical transaction-log topology for a database recovery generation, including TLogs, log routers, backup workers, locality policy, epoch boundaries, and compatibility metadata.

## Important APIs, Types, And Functions
`OptionalInterface<T>` stores a stable `UID` plus optional full endpoint interface. `TLogSet` describes one DC/locality set of TLogs, log routers, backup workers, anti-quorum, replication factor, policy, localities, `TLogVersion`, and tag locations. `OldTLogConf` captures prior generations. `LogSystemConfig` stores current sets, old sets, log-router/tag counts, epoch, recruitment ID, locked TLog IDs, and range-backup tags, with helpers such as `allLocalLogs`, `allPresentLogs`, `hasTLog`, `hasLogRouter`, `hasBackupWorker`, and `getEpochEndVersion`.

## Control Flow
Recovery code builds a new `LogSystemConfig`, compares it with previous generations, recruits/logs roles based on its sets, and publishes it via `ServerDBInfo` and coordinated state. Optional interfaces can be compared by identity even when endpoints are absent.

## State And Persistence Behavior
This is persisted cluster metadata in coordinated state and broadcasts. Serialization gates `rangeBackupWorkerTags` for non-FlatBuffer archives using `protocolVersion().hasRangeBackupWorker()` while FlatBuffers always include all fields.

## Dependencies And Integration Points
It depends on backup and TLog interfaces, replication policies, and `DatabaseConfiguration`. It is consumed by master recovery, cluster controller recruitment, TLogs, log routers, backup/range-backup workers, and workers receiving `ServerDBInfo`.

## Risks And Edge Cases
Serialization compatibility is the dominant risk. Identity-only equality must not hide endpoint changes when communication availability matters. Old generations and known locked logs must be retained long enough for recovery safety.

## Test Signals
Important signals are log-system serialization across protocol versions, equality/identity comparisons, recovery generation transitions, all-present/all-local log enumeration, and downgrade/upgrade tests around range-backup worker tags.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LogSystemConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MasterInterface.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MasterInterface.h

## Purpose
This header defines the RPC contract between commit proxies, cluster controller, and the master role for commit-version assignment, live committed-version reporting, recovery-data updates, and master lifetime validation.

## Important APIs, Types, And Functions
`MasterInterface` exposes `waitFailure`, `getCommitVersion`, `getLiveCommittedVersion`, `reportLiveCommittedVersion`, and `updateRecoveryData`. Request/reply types include `ChangeCoordinatorsRequest`, `ResolverMoveRef`, `GetCommitVersionRequest/Reply`, `UpdateRecoveryDataRequest`, `ReportRawCommittedVersionRequest`, and `LifetimeToken`. `CommitProxyVersionReplies` stores cached replies by request number with `NotifiedVersion` progress.

## Control Flow
`initEndpoints` registers adjacent endpoints with task priorities; serialization stores `waitFailure` and reconstructs adjusted endpoints on deserialization. Commit proxies request new commit versions, report processed request numbers, receive resolver movement changes, and report raw committed versions back to the master.

## State And Persistence Behavior
The interface is transient, but its messages carry persistent recovery and commit-version state: recovery transaction version, last epoch end, resolver/proxy lists, metadata version, min known committed version, written tags, and master lifetime token.

## Dependencies And Integration Points
It depends on commit proxy/resolver/TLog interfaces, database configuration, version vectors, storage server interfaces, Swift interop, and Flow notified values. It integrates with master recovery, commit proxy batching, live committed-version centralization, and coordinator changes.

## Risks And Edge Cases
Endpoint ordering is hard-coded through adjusted endpoints; adding streams requires careful compatibility. `LifetimeToken` logic protects against stale masters, so comparison bugs can cause split-brain-like behavior. Commit-version reply caching must erase only fully obsolete request numbers.

## Test Signals
Tests should cover endpoint round trips, monotonic commit-version replies, resolver-change propagation, stale lifetime rejection, live committed-version reporting with optional predecessor waiting, and recovery-data updates during master replacement.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MasterInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MoveKeys.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MoveKeys.h

## Purpose
`MoveKeys.h` declares data-distribution shard movement operations and storage-server add/remove helpers. It is the contract for updating system keyspace state during data movement.

## Important APIs, Types, And Functions
`MoveKeysLock` serializes ownership fields used to guard writes. `DDEnabledState` is an in-memory data-distribution mode gate with enabled, snapshot, and blob-restore-preparing states. `MoveKeysParams` bundles data move ID, one range or multiple ranges, destination teams, healthy destinations, flow locks, completion promise, remote flag, relocation interval, cancellation policy, and optional bulk-load task state. Actors include `readMoveKeysLock`, `takeMoveKeysLock`, `checkMoveKeysLock`, `rawStartMovement`, `rawFinishMovement`, `moveKeys`, `cleanUpDataMove`, `addStorageServer`, `removeStorageServer`, `canRemoveStorageServer`, and `removeKeysFromFailedServer`.

## Control Flow
DD takes the move-keys lock, starts movement by updating source/destination metadata, waits for fetch/ready conditions, then finishes movement and cleans old destinations. Removal paths check that no keys remain before deleting server metadata.

## State And Persistence Behavior
These functions mutate FoundationDB system keyspace: shard assignments, server lists, server keys, key servers, data-move metadata, and TSS mappings. `DDEnabledState` itself is process-local and resets on restart.

## Dependencies And Integration Points
It depends on commit transactions, key range maps, Native API, master types, seed shard initialization, storage interfaces, TSS mapping, and bulk-load task state. It is central to data distributor, storage recruitment, failed-server handling, bulk loading, and physical shard movement.

## Risks And Edge Cases
Overlapping moves, stale locks, multiple-range physical shard moves, TSS paired removals, remote DC movement, and DD-disabled modes are high-risk. `keys` and `ranges` are mutually exclusive by convention, so callers must enforce it.

## Test Signals
Simulation should verify lock conflict rejection, start/finish idempotence under retries, cancellation cleanup, failed-server metadata removal, storage-server add/remove versions, TSS mapping correctness, and no data loss during overlapping or retried movements.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MoveKeys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MutationTracking.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MutationTracking.h

## Purpose
This header declares optional debug tracing helpers for targeted mutation and key-range tracking in simulation/debug builds.

## Important APIs, Types, And Functions
`MUTATION_TRACKING_ENABLED` currently defaults to `0`. Macros `DEBUG_MUTATION`, `DEBUG_KEY_RANGE`, and `DEBUG_TAGS_AND_MESSAGE` short-circuit calls to `debugMutation`, `debugKeyRange`, and `debugTagsAndMessage`, which return `TraceEvent` objects.

## Control Flow
When enabled, call sites can emit trace events for mutations, key ranges, or tagged commit blobs. The comments note that range/tag helpers log only the first occurrence of a tracked key.

## State And Persistence Behavior
There is no durable state. The tracked-key set is defined in the implementation file to reduce recompilation, and output is trace logging only.

## Dependencies And Integration Points
It depends on FDB types, commit transaction structures, and Flow tracing. Integration points are mutation handling, commit proxy/TLog/storage paths, and simulation debugging.

## Risks And Edge Cases
Because the macros use boolean short-circuiting with `TraceEvent` expressions, enabling tracking can affect compile-time and runtime behavior if misused. Logging only first occurrences can hide repeated corruption patterns.

## Test Signals
Test signals are mostly diagnostic: compile with tracking enabled, confirm targeted events appear for selected keys, and verify disabled builds do not emit or pay meaningful overhead.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MutationTracking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/OTELSpanContextMessage.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/OTELSpanContextMessage.h

## Purpose
This file defines a reserved log-stream message carrying an OpenTelemetry-style `SpanContext` so TLogs and storage servers can associate subsequent mutations with a transaction trace context.

## Important APIs, Types, And Functions
`OTELSpanContextMessage` stores `SpanContext spanContext`, serializes a leading `MutationRef::Reserved_For_OTELSpanContextMessage` byte plus the context, and provides `toString`, `startsOTELSpanContextMessage`, and `isNextIn`.

## Control Flow
Commit code can push the message before mutation payloads. Consumers peek the first byte, identify the metadata message, deserialize the span context, and apply it to following mutations until superseded.

## State And Persistence Behavior
The message is persisted in transaction logs as stream metadata. It changes tracing attribution but not database contents.

## Dependencies And Integration Points
It depends on `fdbclient/Tracing.h`, FDB types, commit transactions, and mutation reserved type codes. It integrates with TLog serialization, storage-server log replay, and distributed tracing.

## Risks And Edge Cases
Reserved-byte uniqueness is critical. Mixing legacy `SpanContextMessage` and OTEL contexts requires consumers to handle both. Trace metadata should not be allowed to corrupt mutation framing.

## Test Signals
Tests should cover marker-byte detection, serialization round trips, mixed mutation/metadata streams, and trace attribution through TLog peek and storage replay.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/OTELSpanContextMessage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/PartitionMapMessage.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/PartitionMapMessage.h

## Purpose
`PartitionMapMessage.h` defines the reserved transaction-log metadata message that carries backup partition-map information from commit proxies to backup workers.

## Important APIs, Types, And Functions
`PartitionMapMessage` wraps a `PartitionMap`, serializes a leading `MutationRef::Reserved_For_PartitionMapMessage` byte and the map, and exposes `toString`, `startsPartitionMapMessage`, and `isNextIn`.

## Control Flow
Commit proxies inject the message into log streams. Consumers discriminate it by peeking the first byte and then update per-tag key-range partition knowledge for backup processing.

## State And Persistence Behavior
The partition map is persisted in the log stream, but this header has no standalone persistent state. It controls how backup workers interpret subsequent tagged mutations.

## Dependencies And Integration Points
It depends on commit transaction types and `BackupPartitionMap.h`. It integrates with backup workers, commit proxies, and TLog stream readers.

## Risks And Edge Cases
The leading reserved byte must not collide with mutation types or other metadata messages. Large partition maps can increase log message size and backup catch-up cost.

## Test Signals
Useful tests verify marker detection, map serialization, backup worker consumption, compatibility with ordinary mutations in the same stream, and behavior when partition maps change while backup is running.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/PartitionMapMessage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/QuietDatabase.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/QuietDatabase.h

## Purpose
This header declares helper actors used by tests and operational workflows to determine whether a database is quiet, inspect queues, get workers/storage servers, and perform simulation-only recovery/reconfiguration actions.

## Important APIs, Types, And Functions
Important functions include `getDataInFlight`, `getTLogQueueInfo`, `getMaxStorageServerQueueSize`, `getDataDistributionQueueSize`, `getTeamCollectionValid`, `getStorageServers`, `getWorkers`, `getMasterWorker`, `repairDeadDatacenter`, `reconfigureAfter`, `getStorageWorkers`, `getCoordWorkers`, `enableConsistencyScanInSim`, `disableConsistencyScanInSim`, `disableDDPipelineControl`, and `isDDPipelineControlEnabled`.

## Control Flow
Callers pass a `Database` and usually an `AsyncVar<ServerDBInfo>`; implementations query system keyspace and role interfaces, then aggregate queue/worker state. Simulation helpers alter consistency-scan or DD-pipeline behavior for test completion.

## State And Persistence Behavior
Most functions read cluster state. `repairDeadDatacenter` and `reconfigureAfter` can mutate configuration state. DD pipeline control is a plain process-local boolean intended for test harnesses.

## Dependencies And Integration Points
It depends on database context, Native API, tester and worker interfaces, storage-server interfaces, and `ServerDBInfo`. It integrates with workload tests, consistency checking, DD quiescence, and database recovery tests.

## Risks And Edge Cases
These helpers can observe changing cluster state and may race recovery or recruitment. Simulation-only switches should not leak into production behavior. Queue estimates depend on role availability and current `ServerDBInfo`.

## Test Signals
Signals include quiet-database waits completing after workloads, accurate queue-size aggregation, correct worker filtering flags, reconfigure-after timing, and successful consistency-scan enable/disable in simulation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/QuietDatabase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RatekeeperInterface.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RatekeeperInterface.h

## Purpose
This header defines the RPC interface for the ratekeeper role, which supplies transaction rate limits, health metrics, client tag throttles, commit-cost estimates, and storage-server version lag.

## Important APIs, Types, And Functions
`RatekeeperInterface` exposes `waitFailure`, `getRateInfo`, `haltRatekeeper`, `reportCommitCostEstimation`, and `getSSVersionLag`. `TransactionCommitCostEstimation` aggregates operation and cost sums. `GetRateInfoRequest/Reply` exchange released transaction counts, throttled tag counts, detail level, transaction/batch rates, lease duration, health metrics, and optional client throttles. Other messages include `HaltRatekeeperRequest`, `ReportCommitCostEstimationRequest`, and `GetSSVersionLagRequest/Reply`.

## Control Flow
GRV proxies periodically ask for rate info, report how many transactions were released, and receive a lease-backed limit. Storage/commit paths can report tag commit-cost estimates. Cluster controller can halt or wait on the role.

## State And Persistence Behavior
The interface is transient. The data reflects in-memory ratekeeper calculations and health metrics, not persisted state, although throttling decisions influence committed workload throughput.

## Dependencies And Integration Points
It depends on commit proxy types, health metrics, transaction tags, RPC streams, locality, and FDB types. It integrates with GRV proxies, storage servers, commit-cost estimation, and cluster controller recruitment.

## Risks And Edge Cases
Stale rate leases, missing detailed metrics, huge tag maps, or incorrect cost aggregation can over-throttle or under-throttle clients. `TransactionCommitCostEstimation` must remain consistent with `UpdateCommitCostRequest`.

## Test Signals
Tests should validate rate reply serialization, tag throttle propagation, cost aggregation, ratekeeper failure handling, and primary/remote storage-server lag reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RatekeeperInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RatekeeperLimitReasons.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RatekeeperLimitReasons.h

## Purpose
This header enumerates the reason codes ratekeeper uses when selecting a transaction rate limit.

## Important APIs, Types, And Functions
`limitReason_t` includes `unlimited`, storage-server queue/write/readable/free-space/durability reasons, log-server MVCC/queue/free-space reasons, storage-server list fetch failure, and `limitReason_t_end`. External arrays `limitReasonName` and `limitReasonDesc` map codes to readable diagnostics; `limitReasonEnd` mirrors the enum end.

## Control Flow
Ratekeeper code computes limiting metrics, chooses a reason, and uses the name/description arrays for trace or status output.

## State And Persistence Behavior
There is no mutable or persistent state in the header. The enum values are diagnostic contract state and should remain stable for logs/status consumers.

## Dependencies And Integration Points
It is standalone and integrates with ratekeeper tracing, status JSON, metrics, and operator diagnostics.

## Risks And Edge Cases
Adding enum values requires updating the external arrays in lockstep. Reordering can break dashboards or tooling that interpret numeric reason codes.

## Test Signals
Tests or static checks should ensure `limitReasonEnd` and the name/description arrays match `limitReason_t_end`, and that ratekeeper emits expected reasons under synthetic bottlenecks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RatekeeperLimitReasons.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RecoveryState.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RecoveryState.h

## Purpose
`RecoveryState.h` defines the coarse recovery phase carried in `ServerDBInfo` plus a more detailed status enum used by status reporting.

## Important APIs, Types, And Functions
`enum class RecoveryState` runs from `UNINITIALIZED` through reading/locking coordinated state, recruiting, recovery transaction, writing cstate, accepting commits, all logs recruited, storage recovered, and `FULLY_RECOVERED`. `namespace RecoveryStatus` provides a detailed enum and external `names`/`descriptions` arrays.

## Control Flow
Master and cluster-controller recovery code advances through these states as it reads cluster state, locks old transaction servers, recruits roles, commits recovery mutations, publishes cstate, and waits for logs/storage recovery.

## State And Persistence Behavior
`RecoveryState` is serialized in `ServerDBInfo` and used for live system decisions. `RecoveryStatus` is primarily status output. The values form a wire/status contract.

## Dependencies And Integration Points
It depends only on Flow serialization. It integrates with master recovery, status generation, cluster controller health, and workers consuming `ServerDBInfo`.

## Risks And Edge Cases
The comment warns that `RecoveryState` is decision-bearing and should be changed cautiously. Adding states requires status descriptions and compatibility analysis.

## Test Signals
Recovery simulation should show monotonic/valid state transitions, correct status names/descriptions, and role behavior changing only at the intended recovery phases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RecoveryState.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ResolverInterface.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ResolverInterface.h

## Purpose
This header defines the resolver role RPC interface and conflict-resolution request/reply payloads used by commit proxies.

## Important APIs, Types, And Functions
`ResolverInterface` exposes `resolve`, `metrics`, `split`, `waitFailure`, and `txnState`, with locality and unique ID. `ResolveTransactionBatchRequest` carries span context, version window, transactions, transaction-state transaction offsets, written tags, and last shard move. `ResolveTransactionBatchReply` returns per-transaction commit flags, state mutations, conflicting read ranges, private mutations by TLog location, two-phase commit version map, written tags, and last shard move. Metrics and split APIs are `ResolutionMetricsRequest/Reply` and `ResolutionSplitRequest/Reply`.

## Control Flow
Commit proxies send batches to resolvers for conflict checking. Resolvers reply with commit/abort decisions and private mutation payloads. Metrics and split requests support load and shard-boundary decisions.

## State And Persistence Behavior
Requests are transient, but resolver state tracks key conflict ranges and system transaction mutations across versions. Replies feed durable TLog commits.

## Dependencies And Integration Points
It depends on commit proxy interfaces, commit transaction structures, timed requests, locality, and RPC. It integrates with commit proxies, master recovery transaction-state broadcasts, data movement, and DD split logic.

## Risks And Edge Cases
Version ordering, arena lifetime, private mutation counts, conflicting range IDs, and two-phase commit maps are correctness-critical. Resolver endpoint load-balance flags affect routing freshness.

## Test Signals
Signals include conflict checking correctness, committed vector size matching input transactions, private mutation serialization, split-key metrics, transaction-state replay, and resolver failure/recruitment behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ResolverInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RocksDBCheckpointUtils.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RocksDBCheckpointUtils.h

## Purpose
This header declares RocksDB-specific checkpoint metadata, SST reader/writer abstractions, and checkpoint fetch/read/delete helpers used by data movement and storage recovery paths.

## Important APIs, Types, And Functions
Interfaces include `ICheckpointByteSampleReader`, `IRocksDBSstFileWriter`, and `IRocksDBSstFileReader`. Metadata types include `CheckpointFile`, `SstFileMetaData`, `LiveFileMetaData`, `RocksDBColumnFamilyCheckpoint`, `RocksDBCheckpoint`, and `RocksDBCheckpointKeyValues`. Functions include `fetchRocksDBCheckpoint`, `getTotalFetchedBytes`, `deleteRocksCheckpoint`, `newRocksDBCheckpointReader`, `newCheckpointByteSampleReader`, `newRocksDBSstFileWriter`, `newRocksDBSstFileReader`, and typed accessors `getRocksCF`, `getRocksCheckpoint`, and `getRocksKeyValuesCheckpoint`.

## Control Flow
Checkpoint fetchers copy RocksDB checkpoint files to a local directory and may call a progress callback so retries can resume. Readers expose either chunks, key-values, byte samples, or range-restricted SST reads.

## State And Persistence Behavior
The metadata serializes file paths, logical ranges, sizes, RocksDB live-file fields, checksums, sequence numbers, levels, fetched flags, and target ranges. It represents on-disk checkpoint files and fetch progress.

## Dependencies And Integration Points
It depends on Native API, `ServerCheckpoint`, Flow futures, RocksDB metadata conventions, and `CheckpointMetaData`. It integrates with `IKeyValueStore::checkpoint`, physical shard/data movement, checkpoint transfer, and RocksDB SST ingestion.

## Risks And Edge Cases
Path handling, checksum/metadata drift from RocksDB upstream, resumable fetch consistency, range tombstone bounds, and logical-vs-file byte accounting are risky. Deprecated fields remain for compatibility.

## Test Signals
Tests should validate metadata serialization, fetch resume after interruption, logical byte totals, range-restricted reads, SST writer/reader round trips, checksum validation, and cleanup of fetched checkpoint files.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RocksDBCheckpointUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/SeedShardServers.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/SeedShardServers.h

## Purpose
This small header declares the helper that seeds the initial shard-server mappings into the first database transaction.

## Important APIs, Types, And Functions
`seedShardServers(Arena& arena, CommitTransactionRef& tr, std::vector<StorageServerInterface> servers)` mutates a commit transaction to establish initial key/server assignments.

## Control Flow
Master initialization passes an arena, commit transaction, and recruited seed storage servers. The implementation writes the required system-key mutations into the transaction.

## State And Persistence Behavior
The function creates durable initial system keyspace state when the first transaction commits. It has no state of its own.

## Dependencies And Integration Points
It depends on commit transaction and storage-server interface types. It is called from initial cluster creation/recovery paths before ordinary `addStorageServer` flows are used.

## Risks And Edge Cases
Incorrect seeding can leave system key ranges unassigned or inconsistently replicated. The arena must outlive mutations stored in the commit transaction.

## Test Signals
Initial database creation tests should verify all keyspace ranges are assigned to seed servers, storage server tags are correct, and recovery can read the resulting system keyspace.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/SeedShardServers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ServerCheckpoint.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ServerCheckpoint.h

## Purpose
`ServerCheckpoint.h` defines generic checkpoint reader/fetch/delete interfaces independent of a particular storage engine.

## Important APIs, Types, And Functions
`FDB_BOOLEAN_PARAM(CheckpointAsKeyValues)` controls checkpoint materialization mode. `ICheckpointIterator` batches key-value reads. `ICheckpointReader` supports `init`, `nextKeyValues`, `nextChunk`, `close`, optional `getIterator`, and `inUse`. Factory and utility functions include `newCheckpointReader`, `deleteCheckpoint`, `fetchCheckpoint`, `fetchCheckpointRanges`, `serverCheckpointDir`, and `fetchedCheckpointDir`.

## Control Flow
Fetch functions copy or convert checkpoint data to local directories, optionally checkpointing progress through a callback. Readers stream checkpoint contents as raw chunks or key-value batches, and implementations can expose range iterators.

## State And Persistence Behavior
The header operates over `CheckpointMetaData`, which records durable checkpoint identity, format, and locations. Directory helpers standardize server-side and fetched-checkpoint paths.

## Dependencies And Integration Points
It depends on Native API, storage checkpoint metadata, Flow futures, and storage-engine-specific implementations such as RocksDB checkpoint utilities. It integrates with data movement, recovery, backup/restore, and storage checkpoint transfer.

## Risks And Edge Cases
Incorrect format dispatch, lifecycle of raw `ICheckpointReader*`, progress callback failures, partial fetches, and chunk/key-value mode mismatches can corrupt movement or leak disk files.

## Test Signals
Tests should cover fetch resume, range fetch, directory naming, reader close behavior, chunk and key-value iteration, delete cleanup, and dispatch to each supported checkpoint format.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ServerCheckpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ServerDBInfo.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ServerDBInfo.h

## Purpose
This header defines `ServerDBInfo`, the transient database metadata broadcast to workers so server roles can locate the cluster controller, master, proxies, resolvers, logs, ratekeeper, data distributor, consistency scan, and client-facing database info.

## Important APIs, Types, And Functions
`ServerDBInfo` stores an update `id`, `ClusterControllerFullInterface`, `ClientDBInfo`, optional distributor/ratekeeper/consistency-scan interfaces, `MasterInterface`, resolver list, recovery count/state, master lifetime, log system config, prior committed log servers, optional latency-band config, and info generation. `UpdateServerDBInfoRequest` carries serialized DB info and endpoint broadcast data; `GetServerDBInfoRequest` asks the controller for a newer value. `broadcastTxnRequest` and `broadcastDBInfoRequest` fan out updates.

## Control Flow
Cluster controller/master update `ServerDBInfo`, workers receive broadcasts through `WorkerInterface.updateServerDBInfo`, and stale workers can request the current value by known ID.

## State And Persistence Behavior
The object is transient and not client-visible, but it mirrors recovery/coordinated-state decisions. `myLocality` is explicitly not serialized.

## Dependencies And Integration Points
It depends on data distributor, consistency scan, latency bands, log system, master, ratekeeper, recovery, and worker interfaces. It is a central integration point for nearly all server roles.

## Risks And Edge Cases
Missing or stale `ServerDBInfo` causes workers to contact obsolete roles. Serialization changes have broad compatibility impact. `priorCommittedLogServers` must keep old logs alive while recovery is not fully committed.

## Test Signals
Signals include broadcast fanout counts, stale known-ID behavior, role replacement updates, recovery-state propagation, latency-band propagation, and correct omission of local-only data.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ServerDBInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ShardMetrics.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ShardMetrics.h

## Purpose
This header defines lightweight data structures for tracking aggregate metrics of a shard while data distribution observes size, bandwidth, and usable-region state.

## Important APIs, Types, And Functions
`ShardMetrics` contains `StorageMetrics metrics`, `lastLowBandwidthStartTime`, and `shardCount`, with equality comparison and constructor. `ShardTrackedData` bundles futures for shard, byte, and usable-region tracking plus an `AsyncVar<Optional<ShardMetrics>>` stats handle.

## Control Flow
DD tracking actors update the futures and async stats value. Consumers read `stats` to decide split/merge/movement actions.

## State And Persistence Behavior
All state is in memory. `shardCount` records aggregation over smaller shards but is not durable.

## Dependencies And Integration Points
It depends on storage-server interfaces for `StorageMetrics` and Flow futures/async variables. It integrates with DD shard tracking, shard split/merge logic, and load balancing.

## Risks And Edge Cases
Equality compares double timestamps exactly, which is appropriate for state comparison but fragile for computed values. Cancelled tracking futures or absent stats can stall DD decisions.

## Test Signals
Tests should observe DD behavior under changing storage metrics, low-bandwidth timing, aggregation over multiple shards, and cancellation/cleanup of tracking actors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ShardMetrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ShardSizing.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ShardSizing.h

## Purpose
`ShardSizing.h` declares helpers for computing permitted shard size and I/O bounds used by data distribution split/merge decisions.

## Important APIs, Types, And Functions
`ShardSizeBounds` contains `StorageMetrics max`, `min`, and `permittedError`, equality comparison, and `shardSizeBoundsBeforeTrack`. Functions `getShardSizeBounds`, `getMaxShardSize`, and `ddLargeTeamEnabled` compute bounds from key ranges, database-size estimates, and feature knobs.

## Control Flow
DD asks for size bounds before or during shard tracking, compares live `StorageMetrics` to min/max/error windows, and uses the result to split large/hot shards or merge small/cold ones.

## State And Persistence Behavior
The file has no state. Computed values influence persistent data movement and shard-boundary mutations elsewhere.

## Dependencies And Integration Points
It depends on FDB types and `StorageMetrics`. It integrates with DD queueing, shard metrics, team sizing, and large-team behavior.

## Risks And Edge Cases
Incorrect bounds can cause excessive shard churn, oversized shards, or missed hot-shard splits. `ddLargeTeamEnabled` must reflect configuration consistently across DD actors.

## Test Signals
Tests should cover boundary formulas for small and large database estimates, before-track defaults, large-team enablement, and split/merge decisions around permitted error thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ShardSizing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/SpanContextMessage.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/SpanContextMessage.h

## Purpose
This header defines the legacy span-context metadata message embedded in transaction-log streams to associate subsequent mutations with a `SpanID`.

## Important APIs, Types, And Functions
`SpanContextMessage` stores `SpanID spanContext`, serializes a leading `MutationRef::Reserved_For_SpanContextMessage` byte and the span ID, and provides `toString`, `startsSpanContextMessage`, and `isNextIn`.

## Control Flow
Writers place the marker before mutation messages; readers peek one byte, detect the reserved message, deserialize the span ID, and attach trace context to following mutations.

## State And Persistence Behavior
The message is persisted in TLogs as trace metadata only. It does not affect key-value contents.

## Dependencies And Integration Points
It depends on FDB and commit transaction types, mutation reserved bytes, TLog readers, storage-server replay, and tracing infrastructure.

## Risks And Edge Cases
It overlaps conceptually with `OTELSpanContextMessage`; consumers must handle both encodings. Reserved-byte collisions or incorrect peeking break log stream framing.

## Test Signals
Test signals include marker detection, serialization round trip, mixed metadata/mutation streams, and trace context visibility during storage recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/SpanContextMessage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/StorageMetrics.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/StorageMetrics.h

## Purpose
`StorageMetrics.h` declares storage-server metric sampling, wait-metrics notification, range splitting, read-hot-range reporting, and generic serving loops for storage metrics RPCs.

## Important APIs, Types, And Functions
It defines histogram names, `StorageMetricSample`, `TransientStorageMetricSample`, `WaitMetricsMapHighWatermarks`, `StorageServerMetrics`, `ByteSampleInfo`, `isKeyValueInSample`, `CommonStorageCounters`, and `IStorageMetricsService`. `StorageServerMetrics` exposes metric estimation, notifications for reads/writes/not-readable ranges, polling, split metrics, storage metrics replies, wait metrics, read-hot ranges, hot shard counts, and split points. `serveStorageMetricsRequests` races request-serving coroutines and polling.

## Control Flow
Storage server code records sampled byte/read/write metrics by key, expires transient samples, notifies waiters in a `KeyRangeMap`, and serves request streams from `StorageServerInterface`. Split and hot-range methods use samples to choose keys or ranges.

## State And Persistence Behavior
Metrics are in-memory and approximate. They affect durable DD decisions indirectly by driving shard splits, merges, movement, and throttling.

## Dependencies And Integration Points
It depends on FDB types, simulator, unit tests, storage-server interfaces, key range maps, server knobs, Flow counters, and request streams. It integrates with storage servers, DD, ratekeeper, fetchKeys, and status/metrics.

## Risks And Edge Cases
Sampling probability invariants, high-watcher wait maps, stale transient samples, empty/not-readable ranges, and split-key math are risky. Knob-dependent units must stay consistent with storage and DD expectations.

## Test Signals
Tests should cover byte-sample probability/estimation, waitMetrics notification and timeout behavior, split points, hot-range detection, high-watermark tracing, and service loops handling each request stream.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/StorageMetrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TLogInterface.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TLogInterface.h

## Purpose
This header defines the transaction-log role RPC interface and message types for peeking, popping, committing, locking, metrics, snapshots, recovery completion, and recovery tracking.

## Important APIs, Types, And Functions
`TLogInterface` exposes streams for `peekMessages`, `peekStreamMessages`, `popMessages`, `commit`, `lock`, queue metrics, confirm running, wait failure, recovery finished, pop disable/enable, snapshot, and recovery tracking. Message types include `TLogLockResult`, `UnknownCommittedVersions`, `VerUpdateRef`, `TLogPeekRequest/Reply`, `TLogPeekStreamRequest/Reply`, `TLogPopRequest`, `TagMessagesRef`, `TLogCommitRequest/Reply`, `TLogQueuingMetricsRequest/Reply`, `TLogDisablePopRequest`, `TLogEnablePopRequest`, `TLogSnapRequest`, and `TrackTLogRecoveryRequest/Reply`.

## Control Flow
Commit proxies send `TLogCommitRequest` batches with versions and serialized messages. Storage servers/log routers peek from a begin version by tag, optionally through streaming replies. Consumers pop durable versions. Recovery locks logs, discovers unknown committed versions, confirms running logs, and waits for old generations to recover.

## State And Persistence Behavior
Requests carry durable log versions, known committed versions, message blobs, tag locations, snapshot IDs, and queue metrics. Endpoint serialization stores one base endpoint and reconstructs adjusted endpoints by fixed index.

## Dependencies And Integration Points
It depends on FDB types, commit transactions, timed requests, storage bytes, span context, and RPC streams. It is central to master recovery, commit proxies, storage servers, log routers, backup, snapshots, and ratekeeper queue metrics.

## Risks And Edge Cases
Endpoint index ordering is compatibility-critical. Version chain gaps, incorrect popped versions, unknown committed versions, sequence IDs, and streaming acknowledgement handling can break recovery or durability.

## Test Signals
Signals include commit/peek/pop ordering, recovery lock correctness, log router and storage catch-up, queue metrics accuracy, disable/enable pop around snapshots, streaming peek backpressure, and old-generation recovery tracking.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TLogInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TSSMappingUtil.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TSSMappingUtil.h

## Purpose
This header declares helpers for reading the current test storage server (TSS) to storage server mapping from system keyspace.

## Important APIs, Types, And Functions
`readTSSMappingRYW` reads the mapping through a `ReadYourWritesTransaction`; `readTSSMapping` reads it through a lower-level `Transaction`. Both fill `std::map<UID, StorageServerInterface>*`.

## Control Flow
Data movement or recruitment code calls the appropriate helper within an existing transaction, then uses the resulting map to account for TSS pairings.

## State And Persistence Behavior
The functions read persistent system keyspace mapping data but do not declare state of their own.

## Dependencies And Integration Points
It depends on RYW transactions and storage-server interfaces. It integrates with `MoveKeys`, TSS recruitment/removal, DD, and testing of storage shadowing.

## Risks And Edge Cases
Callers must pass a live transaction and handle retries. Stale mappings can lead to incorrect TSS pairing during movement or removal.

## Test Signals
Tests should validate mapping reads under both transaction types, empty mappings, TSS add/remove transitions, and retry behavior during concurrent mapping updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TSSMappingUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TesterInterface.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TesterInterface.h

## Purpose
`TesterInterface.h` declares the RPC contracts used by simulation/tester workers to recruit and drive workloads.

## Important APIs, Types, And Functions
`CheckReply` wraps a boolean. `WorkloadInterface` exposes setup, start, check, metrics, and stop request streams. `WorkloadRequest` carries workload title, timeout, database ping delay, shared random number, database usage flag, compound workload option lists, ranges to check, client index/count, failure workload controls, and a reply with `WorkloadInterface`. `TesterInterface` exposes a recruitment stream.

## Control Flow
The tester recruits workload actors on clients, sends setup/start/check/metrics/stop messages through the returned workload interface, and coordinates multiple clients by shared random number and client counts.

## State And Persistence Behavior
The interface is transient test control state. Workloads may mutate the database, but the request metadata itself is not persistent.

## Dependencies And Integration Points
It depends on RPC, performance metrics, Native API, arenas, and FDB key/value option encoding. It integrates with simulation test workloads and worker recruitment.

## Risks And Edge Cases
Arena-backed `StringRef` and option vectors require correct lifetime management. Failure-workload disabling and `rangesToCheck` must serialize consistently across testers.

## Test Signals
Simulation test harnesses validate recruitment, workload lifecycle ordering, metrics collection, check replies, multi-client option propagation, and failure-injection toggles.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TesterInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WaitFailure.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WaitFailure.h

## Purpose
This header declares reusable actors for server-role failure detection through `waitFailure` request streams.

## Important APIs, Types, And Functions
`waitFailureServer` serves a stream of `ReplyPromise<Void>` waiters. `waitFailureClient`, `waitFailureClientStrict`, and `waitFailureTracker` watch a remote waitFailure stream with configurable reaction time, slope, tracing, trace message, and task priority.

## Control Flow
Server roles expose a waitFailure endpoint and keep requests pending until they fail or stop. Clients issue requests and use delay/reaction settings to convert endpoint failure into actor completion or an `AsyncVar<bool>` update.

## State And Persistence Behavior
There is no persistent state. Failure observations are transient and affect role liveness decisions.

## Dependencies And Integration Points
It depends on `fdbrpc` and Flow futures. It integrates with master, TLog, resolver, ratekeeper, worker, and other role interfaces that include a `waitFailure` stream.

## Risks And Edge Cases
Too-short reaction windows cause false positives; too-long windows delay recovery. Strict and non-strict clients differ in tolerance and must match role semantics.

## Test Signals
Tests should verify failure detection after endpoint shutdown, reaction delays/slopes, tracker async updates, trace emission, and task-priority behavior under load.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WaitFailure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkerEvents.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkerEvents.h

## Purpose
`WorkerEvents.h` declares a helper for collecting the latest trace event fields for a named event across workers.

## Important APIs, Types, And Functions
`WorkerEvents` is a `std::map<NetworkAddress, TraceEventFields>`. `latestEventOnWorkers` takes `std::vector<WorkerDetails>` and an event name, returning an async optional pair of collected events and a set of missing/error worker identifiers.

## Control Flow
The implementation likely sends `EventLogRequest` messages to worker interfaces, collects replies keyed by worker network address, and returns absent data when no events are available.

## State And Persistence Behavior
The helper reads in-memory/latest trace event state on workers. It does not persist anything.

## Dependencies And Integration Points
It depends on tracing fields and `WorkerInterface.actor.h`. It integrates with status/debug tooling and test harnesses that inspect worker event logs.

## Risks And Edge Cases
Workers can fail, omit the requested event, or race log rotation. Network addresses are map keys, so address changes or duplicates can affect aggregation.

## Test Signals
Tests should validate successful collection, missing-event reporting, worker failure handling, and deterministic map contents for multiple workers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkerEvents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkerInterface.actor.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkerInterface.actor.h

## Purpose
This large header defines the worker and cluster-controller RPC contracts used to recruit every server role, register workers, broadcast database info, run diagnostics, execute snapshots, and support testing.

## Important APIs, Types, And Functions
`WorkerInterface` embeds `ClientWorkerInterface`, locality, recruitment streams for TLog/master/proxies/DD/ratekeeper/consistency scan/resolver/storage/log router/backup/range backup, diagnostic streams, waitFailure, exec/snapshot/disk-store streams, DB info updates, and `TesterInterface`. `WorkerDetails` adds process class and health flags. `ClusterControllerFullInterface` extends client cluster interface with recruitment, registration, worker list, DB info, health, TLog rejoin, backup done, coordinator changes, and encryption mode. Many request/reply structs define role recruitment and worker operations. `Role`, `startRole`, `endRole`, `traceRole`, `openDBOnServer`, DB locality helpers, and `ioTimeoutError`/`ioDegradedOrTimeoutError` are declared/defined.

## Control Flow
Workers initialize endpoints, register with the cluster controller, receive role initialization requests, return role interfaces, and handle DB info updates. Cluster controller recruits sets of workers based on configuration and process class, while roles use helper actors for timeout/degraded handling.

## State And Persistence Behavior
Most state is transient RPC/interface state. Requests carry recovery epochs, versions, log tags, encryption modes, storage types, worker health, and snapshot payloads that control durable role behavior. Serialization order is a wire contract.

## Dependencies And Integration Points
It depends on backup, DD, master, TLog, ratekeeper, consistency scan, resolver, storage, tester, log system, recovery state, client worker, and actorcompiler headers. It is the central role-recruitment integration point.

## Risks And Edge Cases
Endpoint initialization omissions, serialization reordering, stale cluster-controller generations, dropped init replies in simulation, worker health false positives, and timeout fault injection can destabilize recovery. `ioTimeoutError` adjusts simulation time before speedup and can inject faults for unreliable processes.

## Test Signals
Simulation should cover role recruitment for every role, worker registration updates, TLog rejoin, backup completion, encryption mode queries, snapshot/exec/disk-store requests, worker health reporting, and I/O timeout/degraded paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkerInterface.actor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkloadKeys.h -->
# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkloadKeys.h

## Purpose
This header declares helpers for mapping floating-point positions to deterministic test keys and back.

## Important APIs, Types, And Functions
`doubleToTestKey(double p)` and `testKeyToDouble(const KeyRef& p)` convert between a double and a key. Prefix overloads `doubleToTestKey(double p, const KeyRef& prefix)` and `testKeyToDouble(const KeyRef& p, const KeyRef& prefix)` scope the conversion under a key prefix.

## Control Flow
Workloads choose numeric positions, convert them to ordered keys, and later decode keys back into numeric positions for validation or distribution logic.

## State And Persistence Behavior
There is no state. Generated keys may be written by workloads and therefore must be stable across processes and runs.

## Dependencies And Integration Points
It depends only on FDB key types. It integrates with simulation workloads, consistency checks, and benchmark keyspace generation.

## Risks And Edge Cases
Floating-point precision, ordering preservation, prefix stripping, and invalid key inputs are the main risks. The conversion must be deterministic across platforms.

## Test Signals
Tests should verify round trips, monotonic ordering, prefix behavior, boundary values, and malformed input handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkloadKeys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coroimpl/CoroFlow.actor.cpp -->
# sources/storage-engines/foundationdb/fdbserver/coroimpl/CoroFlow.actor.cpp

## Purpose
This file implements `CoroThreadPool` using Boost.Coroutine2 so blocking-style thread-pool receivers can interoperate with Flow futures without native OS threads.

## Important APIs, Types, And Functions
`Coroutine` wraps a Boost `pull_type`/`push_type` pair, fixed 256 KiB stack, `start`, `unblock`, `waitFor`, `switcher`, `entry`, and `block`. `WorkPool<Threadlike, Mutex, IS_CORO>` implements `IThreadPool` with nested `Pool` and `Worker`. Public methods are `getError`, `addThread`, `post`, `stop`, `isCoro`, `addref`, and `delref`. `CoroThreadPool::waitFor`, `init`, and `createThreadPool` complete the integration.

## Control Flow
`addThread` creates a worker coroutine and starts it after a zero-delay yield so Net2 is running. Workers initialize user data, take queued `PThreadAction`s, execute them, yield between actions, and block when idle. `post` queues work and unblocks one idle coroutine. `stop` cancels queued actions, marks workers stopped, unblocks idle workers, and returns the all-stopped future.

## State And Persistence Behavior
State is process-local: current coroutine pointer, work queue, idle/worker lists, actor collections for errors/stops, and user data. There is no persistence.

## Dependencies And Integration Points
It depends on `CoroFlow.h`, `ActorCollection`, metrics/tracing, simulator process info, Boost.Coroutine2, Flow network, and actorcompiler. It provides an `IThreadPool` implementation for components expecting a thread-pool API.

## Risks And Edge Cases
Coroutine lifetime is guarded by a shared `alive` flag because the switcher actor can outlive `Coroutine`. Error propagation stops the pool. `CoroThreadPool::waitFor` asserts it runs inside a coroutine and rethrows future errors after resumption. Stack size and action cancellation callbacks are sensitive.

## Test Signals
Signals include posted actions executing in order, idle wakeups, error propagation stopping the pool, clean deletion of user data, stop completion, future-error rethrowing, and simulation reboot traces not hanging.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coroimpl/CoroFlow.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coroimpl/CoroFlowCoro.actor.cpp -->
# sources/storage-engines/foundationdb/fdbserver/coroimpl/CoroFlowCoro.actor.cpp

## Purpose
This file is the older libcoroutine-based `CoroThreadPool` implementation, used on Windows until Boost.Context is available in CI.

## Important APIs, Types, And Functions
Global `current_coro`, `main_coro`, and `swapCoro` manage coroutine switching. `Coroutine` wraps raw `Coro*`, with `start`, `unblock`, `block`, `wrapRun`, and static `entry`. The same `WorkPool<Threadlike, Mutex, IS_CORO>` pattern implements `IThreadPool`. `coroSwitcher` waits on a Flow future then switches back to a coroutine. `CoroThreadPool::waitFor`, `init`, and `createThreadPool` expose the API.

## Control Flow
`init` creates and initializes the main coroutine. Worker coroutines run the same queue loop as the Boost implementation: initialize user data, execute queued actions, yield, block when idle, and stop on errors or explicit shutdown. `waitFor` schedules `coroSwitcher`, switches to `main_coro`, and resumes once the future is ready.

## State And Persistence Behavior
All state is process-local coroutine scheduler state and work-pool queues. There is no durable state.

## Dependencies And Integration Points
It depends on `Coro.h`, Flow actors, simulator info, tracing, and `CoroFlow.h`. It is a platform-specific implementation behind the same `IThreadPool` contract as the Boost version.

## Risks And Edge Cases
Manual coroutine switching is fragile: `current_coro`/`main_coro` must be initialized, `waitFor` cannot run on the main coroutine, and future errors are only asserted ready here rather than explicitly rethrown. Allocation failure maps to `platform::outOfMemory`.

## Test Signals
Tests should match the Boost implementation: action execution, idle unblocking, stop cleanup, error propagation, future wait/resume behavior, Windows build coverage, and no hangs during simulated reboot timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coroimpl/CoroFlowCoro.actor.cpp -->

# subset-b-008030 Research

Grouped research for the requested Apache Ozone SCM block, command, container, and container balancer files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/ScmBlockDeletingServiceMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/ScmBlockDeletingServiceMetrics.java

## Purpose
Provides Hadoop Metrics2 instrumentation for SCM's background block deleting service. It tracks delete command counts, delete transaction counts, skipped and processed transactions, datanode participation, blocks sent for deletion, live deleted-block-log summaries from `BlockManager`, and per-datanode command outcomes.

## Important APIs, Types, And Functions
`ScmBlockDeletingServiceMetrics` is a singleton `MetricsSource` registered under `SCMBlockDeletingService.class.getSimpleName()`. `create(BlockManager)` registers the metrics instance with `DefaultMetricsSystem`; `unRegister()` clears the singleton and unregisters the source. Increment methods update counters and gauges such as `incrBlockDeletionCommandSent`, `incrBlockDeletionTransactionsOnDatanodes`, `incrBlockDeletionTransactionCompleted`, `incrSkippedTransaction`, `setNumBlockDeletionTransactionDataNodes`, and per-DN `incrDNCommands*` helpers. `getMetrics` snapshots Metrics2 fields and emits extra records from `DeletedBlocksTransactionSummary`. Nested `DatanodeCommandDetails` holds per-datanode sent, success, failure, timeout, and block counts.

## Control Flow
Callers create the singleton during service startup and invoke increment/set methods as delete commands are created, sent, acknowledged, timed out, or completed. Metrics collection calls `getMetrics`, snapshots the annotated mutable counters/gauges, queries `blockManager.getDeletedBlockLog().getTransactionSummary()`, and emits one tagged record for each datanode in `numCommandsDatanode`.

## State And Persistence
State is in-memory metrics state only. The aggregate counters use Metrics2 mutable counters/gauges; per-datanode values live in a `ConcurrentHashMap<DatanodeID, DatanodeCommandDetails>`. The source reads persistent delete-log state indirectly through `BlockManager`, but it does not write SCM metadata.

## Dependencies And Integration Points
Integrates with `SCMBlockDeletingService`, `BlockManager`, the deleted-block log, `HddsProtos.DeletedBlocksTransactionSummary`, Hadoop Metrics2 registry/snapshot APIs, and `DatanodeID`. Observability consumers depend on metric names and tags staying stable.

## Risks And Test Signals
The singleton can retain stale state if `unRegister()` is not called between tests or service restarts. `DatanodeCommandDetails` field increments are not atomic even though the map is concurrent, so concurrent updates to the same datanode can lose increments. `getBNumBlockDeletionCommandFailure` appears to be a typo but may be API-compatible surface. Tests should cover metrics registration/unregistration, aggregate snapshots, per-datanode tagged records, deleted-block-log summary gauges, and concurrent update expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/ScmBlockDeletingServiceMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/package-info.java

## Purpose
Documents the `org.apache.hadoop.hdds.scm.block` package as the SCM area for block location and mapping management.

## Important APIs, Types, And Functions
The file declares only the package and Javadoc. It exports no functions or types, but it establishes package-level documentation for classes such as block managers and block deletion services in the same package.

## Control Flow
There is no runtime control flow. Javadoc tooling consumes the comment while Java compilation associates it with the package.

## State And Persistence
No runtime state and no persistence behavior. It only affects generated documentation and package metadata.

## Dependencies And Integration Points
Its integration point is the Java package system and documentation generation. It must match the package directory and sibling source declarations.

## Risks And Test Signals
Risk is limited to documentation drift or package-name mismatch. Compile and Javadoc generation are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/command/CommandStatusReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/command/CommandStatusReportHandler.java

## Purpose
Handles datanode command status reports on the SCM event bus and routes delete-block command status entries to the block deletion status pipeline.

## Important APIs, Types, And Functions
`CommandStatusReportHandler` implements `EventHandler<CommandStatusReportFromDatanode>`. `onMessage` validates the report and command list, filters `CommandStatus` entries by `SCMCommandProto.Type.deleteBlocksCommand`, and fires `SCMEvents.DELETE_BLOCK_STATUS` with a `DeleteBlockStatus` payload. Nested `CommandStatusEvent` implements `IdentifiableEventPayload` and wraps a list of statuses with an ID from `HddsIdFactory.getLongId()`. `DeleteBlockStatus` adds the reporting `DatanodeDetails`.

## Control Flow
On each report, the handler logs trace details, scans the command statuses, ignores unsupported command types with debug logging, batches all delete-block statuses from the same report, and emits one event if the batch is non-empty. The batching reduces event-thread switching when datanodes report many pending command statuses.

## State And Persistence
The handler is stateless. It creates transient wrapper payloads and does not persist command status itself. Downstream DELETE_BLOCK_STATUS consumers own state updates such as block deletion acknowledgements and metrics.

## Dependencies And Integration Points
Depends on heartbeat dispatcher payloads, protobuf `CommandStatus` and `SCMCommandProto.Type`, SCM event names, the event publisher, datanode identity, and ID generation for event payloads. It is a routing bridge between datanode heartbeat reports and delete-block status handling.

## Risks And Test Signals
Only delete-block command statuses are handled; new command types require explicit routing. Null report/list guards fail fast. Tests should verify batching, unsupported command logging behavior, emitted datanode identity, empty-list no-op behavior, and event IDs being generated for payloads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/command/CommandStatusReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/command/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/command/package-info.java

## Purpose
Documents the `org.apache.hadoop.hdds.scm.command` package as the SCM command-protocol area for commands issued from SCM to datanodes.

## Important APIs, Types, And Functions
The file contains package-level Javadoc and the package declaration only. It exports no executable API.

## Control Flow
There is no runtime control flow. It is consumed by the Java compiler and Javadoc tooling.

## State And Persistence
No runtime state and no persistence. It describes the package role.

## Dependencies And Integration Points
It integrates with Java package metadata and documentation generation. The declared package must remain aligned with sibling SCM command classes.

## Risks And Test Signals
Risk is documentation drift. Compile and Javadoc generation are the practical validation signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/command/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/AbstractContainerReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/AbstractContainerReportHandler.java

## Purpose
Provides shared logic for full and incremental container report handlers. It updates SCM's container stats, lifecycle state, and replica map from datanode-reported `ContainerReplicaProto` records, and emits delete-container commands for stale or invalid replicas.

## Important APIs, Types, And Functions
Subclasses supply `getLogger()`. `processContainerReplica` synchronizes on `ContainerInfo`, updates stats, applies lifecycle transitions, and updates/removes the replica record. `getDetailsForLogging` lazily formats container/replica/datanode details. `updateContainerStats` adjusts sequence ID, used bytes, and key count for healthy replicas with RATIS or EC-specific aggregation. `updateContainerState` maps SCM lifecycle states and replica states to state-machine events or delete commands. `deleteReplica` publishes `DeleteContainerCommand` with the current SCM leader term.

## Control Flow
Replica processing first updates stats when the replica is not unhealthy, invalid, or deleted. RATIS stats compare all replicas; open containers take minimum usage while non-open containers take maximum usage. EC stats consider replica index 1 and parity indexes because other data indexes may be smaller. Then lifecycle handling finalizes OPEN containers when a non-OPEN replica appears, closes CLOSING/QUASI_CLOSED containers on matching closed replicas and BCSID, deletes empty replicas for DELETED containers, force-deletes EC deleted/deleting leftovers, and can resurrect DELETING/DELETED RATIS containers to CLOSED or QUASI_CLOSED when a non-empty valid replica is discovered.

## State And Persistence
The class mutates `ContainerInfo` fields in memory and calls `ContainerManager` for state transitions and replica updates. State transitions may be persisted and replicated by `ContainerStateManager`; replica location updates are in-memory SCM state. Delete-container commands are emitted to the event bus rather than persisted here.

## Dependencies And Integration Points
Depends on `NodeManager`, `ContainerManager`, `SCMContext`, SCM events, datanode command wrappers, `DeleteContainerCommand`, container lifecycle enums, EC replication config, container checksums, and Ratis leader-term access. It is the shared bridge from datanode container reports into SCM container metadata, replication-manager observations, and command dispatch.

## Risks And Test Signals
Concurrency relies on synchronizing the mutable `ContainerInfo`, with a comment noting this should eventually be a container lock. BCSID mismatch handling intentionally skips replica updates in some close paths. DELETING/DELETED resurrection and force-delete behavior are subtle and state-machine bypasses must be tested carefully. Test signals include RATIS and EC stats aggregation, OPEN-to-CLOSING, CLOSING-to-CLOSED, QUASI_CLOSED force close, deleted empty replica deletion, EC orphan deletion, BCSID mismatch logging, not-leader skip behavior, and replica add/remove correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/AbstractContainerReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/CloseContainerEventHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/CloseContainerEventHandler.java

## Purpose
Handles `CLOSE_CONTAINER` events in SCM. It finalizes open containers, builds close-container commands, optionally delays dispatch through a lease, and sends close commands to the datanodes that host the container.

## Important APIs, Types, And Functions
`CloseContainerEventHandler` implements `EventHandler<ContainerID>`. Constructor dependencies are `PipelineManager`, `ContainerManager`, `SCMContext`, optional `LeaseManager<Object>`, and lease timeout. `onMessage` is the main handler. `triggerCloseCallback` publishes `CommandForDatanode<CloseContainerCommand>`. `getContainerToken` pulls an encoded container token from `StorageContainerManager` when available. `getNodes` uses the container pipeline and falls back to current replicas if the pipeline is missing.

## Control Flow
The handler first requires leader SCM. For an OPEN container, it sends `LifeCycleEvent.FINALIZE` to move it to CLOSING. It reloads `ContainerInfo`, and if the state is CLOSING, creates a `CloseContainerCommand` with force enabled for non-RATIS replication, sets leader term and token, then either acquires a lease for delayed callback or publishes immediately when running without a lease manager, such as in Recon tests. Non-CLOSING containers are logged and ignored.

## State And Persistence
The container state transition is persisted through `ContainerManager.updateContainerState`. The lease manager may keep an in-memory scheduled command until timeout. Commands are emitted to the event bus and later queued to datanodes outside this class.

## Dependencies And Integration Points
Integrates with pipeline lookup, container replica lookup, SCM leader context, lease scheduling, container token generation, close-container datanode command protocol, and the SCM event bus.

## Risks And Test Signals
Correctness depends on leader-term access, token generation, and reliable fallback when the original pipeline has been removed. Lease de-duplication may suppress duplicate close events. Tests should cover leader and non-leader behavior, OPEN finalization, CLOSING command emission, lease callback path, missing pipeline fallback to replicas, non-RATIS force flag, token behavior under `StorageContainerManager`, and invalid state handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/CloseContainerEventHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerActionsHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerActionsHandler.java

## Purpose
Routes action requests reported by datanodes to SCM events. Currently it handles datanode requests to close containers.

## Important APIs, Types, And Functions
`ContainerActionsHandler` implements `EventHandler<ContainerActionsFromDatanode>`. `onMessage` iterates protobuf `ContainerAction` entries, converts IDs to `ContainerID`, and fires `SCMEvents.CLOSE_CONTAINER` for `ContainerAction.Action.CLOSE`.

## Control Flow
For each reported action, the handler switches on the action enum. CLOSE logs a debug reason and publishes the container ID for the close handler. Unknown actions are logged as warnings and otherwise ignored.

## State And Persistence
The handler is stateless. It does not update container state directly; downstream close-container processing owns state changes and command dispatch.

## Dependencies And Integration Points
Depends on heartbeat dispatcher `ContainerActionsFromDatanode`, protobuf `ContainerAction`, `DatanodeDetails`, `SCMEvents.CLOSE_CONTAINER`, and the event publisher. It is a narrow bridge from datanode action reports to SCM event handling.

## Risks And Test Signals
Adding new container action types requires switch expansion. Tests should verify one close event per CLOSE action, invalid action warning/no-op behavior, and preservation of the reported container ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerActionsHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManager.java

## Purpose
Defines the SCM container management contract: container allocation, lookup, lifecycle changes, replica tracking, delete transaction updates, matching-container selection for writes, report metrics notification, deletion, reinitialization, and metadata updates.

## Important APIs, Types, And Functions
Key APIs include `reinitialize`, `getContainer`, `getContainers`, `getContainerIDs`, `getContainerStateCount`, `getTotalContainerCount`, `containerExist`, `allocateContainer`, `updateContainerState`, `transitionDeletingOrDeletedToTargetState`, `getContainerReplicas`, `updateContainerReplica`, `removeContainerReplica`, `updateDeleteTransactionId`, `getMatchingContainer`, `notifyContainerReportProcessing`, `deleteContainer`, `getContainerStateManager`, and `updateContainerInfo`.

## Control Flow
The interface separates read/list paths, lifecycle mutation paths, replica mutation paths, allocation paths, and report accounting. Default methods provide all-container listing, total count aggregation over lifecycle states, and a simplified `getMatchingContainer` overload without exclusions.

## State And Persistence
Implementations manage persistent `ContainerInfo` records and in-memory replica state. The interface exposes persistent state transitions and metadata updates, but replica locations are typically report-derived and may not be persisted in the same table.

## Dependencies And Integration Points
Depends on `ReplicationConfig`, `Pipeline`, container lifecycle protobuf enums, `ContainerInfoProto`, and the container table abstraction. It is consumed by SCM protocol handlers, report handlers, replication manager, balancer, block allocation, Recon sync paths, and tests.

## Risks And Test Signals
The contract mixes persisted container state and volatile replica state, so callers must know which changes survive restart. `transitionDeletingOrDeletedToTargetState` explicitly bypasses the normal state machine and needs constrained use. Tests should cover allocation, state transitions, replica update/remove, delete transaction updates, matching-container selection, total count, reinitialization, and report-processing metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManagerImpl.java

## Purpose
Implements the SCM `ContainerManager` facade. It coordinates pipeline selection, container ID generation, persistent container-state mutations, in-memory replica updates, block allocation matching, and container-manager metrics.

## Important APIs, Types, And Functions
The constructor builds a `ContainerStateManagerImpl` through its HA proxy and registers `SCMContainerManagerMetrics`. `allocateContainer(ReplicationConfig, owner)` selects or creates an open pipeline, then calls private `allocateContainer(Pipeline, owner)`. `updateContainerState`, `transitionDeletingOrDeletedToTargetState`, `updateContainerInfo`, and `deleteContainer` delegate locked mutations to `ContainerStateManager`. Replica methods validate existence before delegating. `getMatchingContainer` uses pipeline container IDs, owner filtering, open-container limits, exclusions, and round-robin state-manager matching.

## Control Flow
Allocation first reads open pipelines under the pipeline-manager read lock and local lock. If none exist, it creates a pipeline, opens EC pipelines, waits for readiness, then retries selection. New container creation obtains a sequence ID, checks and records pipeline space, builds `ContainerInfoProto`, and adds it to the state manager. Matching-container selection synchronizes on pipeline ID, may allocate if the pipeline is below its open-container limit, filters by owner and exclusions, and allocates again if no existing container has space.

## State And Persistence
Persistent state is delegated to `ContainerStateManager` and the SCM DB transaction buffer. Replica sets are in-memory state-manager entries. The class also updates metrics for create/delete/list/report outcomes and uses pipeline-manager allocation accounting.

## Dependencies And Integration Points
Depends on `PipelineManager`, `SCMHAManager`, `SequenceIdGenerator`, `ContainerReplicaPendingOps`, `SCMContainerManagerMetrics`, `ContainerStateManagerImpl`, replication configs, and the container table. It sits between SCM APIs/report handlers and the replicated container state manager.

## Risks And Test Signals
Lock ordering with pipeline-manager read locks and the local lock is important for allocation. `allocateContainer` can return null when a selected pipeline lacks space, so callers must handle that. `getContainersForOwner` mutates the navigable set returned by pipeline manager and logs missing container metadata. Tests should cover no-pipeline allocation, EC pipeline opening, pipeline space exhaustion, owner filtering, excluded containers, lifecycle mutation errors, replica validation, delete metrics, and reinitialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplica.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplica.java

## Purpose
Models SCM's in-memory view of a single container replica on a datanode, including replica state, current and origin datanode identity, replica index, BCSID, key count, bytes used, emptiness, and checksums.

## Important APIs, Types, And Functions
`ContainerReplica` is immutable and comparable. Accessors expose container ID, datanode details, origin datanode ID, replica state, sequence ID, key count, bytes used, empty flag, checksums, data checksum, and replica index. `newBuilder()` and `toBuilder()` support construction and copy-modification. Equality and hash code use only `containerID` and `datanodeDetails`; ordering compares those same fields.

## Control Flow
Report handlers construct instances from datanode `ContainerReplicaProto` records and pass them to `ContainerManager.updateContainerReplica` or remove methods. Builder `build()` defaults checksums to `ContainerChecksums.unknown()` when unset.

## State And Persistence
The object is in-memory value state. It is generally stored in SCM's `ContainerStateMap` replica sets and rebuilt from reports after restart. Container metadata persistence is separate from this replica value.

## Dependencies And Integration Points
Depends on `DatanodeDetails`, `DatanodeID`, protobuf replica state, `ContainerChecksums`, and Apache Commons builder helpers. It is consumed by report handling, replication manager, balancer, close command fallback, and placement validation.

## Risks And Test Signals
Because equality ignores state, index, size, sequence ID, and checksum, sets treat a container on a datanode as one replaceable location record. That is intentional for update semantics but risky if multiple replicas of the same container/index could appear on one datanode. Tests should cover builder defaults, origin fallback to current datanode, equality semantics, ordering, `toBuilder`, and checksum propagation from reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplica.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReportHandler.java

## Purpose
Processes full container reports from datanodes. It reconciles the datanode-to-container map, updates SCM's container replica map and stats, handles unknown reported containers, removes replicas missing from the full report, and emits registration-report events.

## Important APIs, Types, And Functions
`ContainerReportHandler` extends `AbstractContainerReportHandler` and implements `EventHandler<ContainerReportFromDatanode>`. The constructor reads `ScmConfig.getUnknownContainerAction()` into `UnknownContainerAction.WARN` or `DELETE`. `onMessage` performs full reconciliation. `processSingleReplica` handles known or unknown replicas. `processMissingReplicas` removes containers missing from the datanode report from both `NodeManager` and `ContainerManager`. `UnknownContainerAction.parse` defaults unknown config strings to WARN.

## Control Flow
The handler resolves the canonical datanode object from `NodeManager`, synchronizes on it to prevent concurrent full and incremental processing, snapshots expected containers from `NodeManager`, then iterates reported replicas. Each known replica reuses the `ContainerID` from `ContainerInfo`, removes it from the expected set, adds new node-manager mappings, clears pending allocation for first confirmation, validates via `ContainerReportValidator`, and delegates to shared replica processing. After the loop, remaining expected IDs are treated as missing and removed. Successful processing increments full-report metrics and registration reports fire a separate registration event.

## State And Persistence
Node-to-container membership is updated in `NodeManager`; container replica state is updated or removed in `ContainerManager`; container lifecycle and stats may persist through shared handler paths. Unknown containers may result in a delete command instead of SCM metadata updates depending on configuration.

## Dependencies And Integration Points
Integrates datanode heartbeat reports, `NodeManager`, `ContainerManager`, `DatanodeInfo` pending allocation tracking, `ContainerReportValidator`, SCM events, registration report handling, and the shared abstract report state machine.

## Risks And Test Signals
Correctness depends on `NodeManager.getContainers` snapshot semantics: modifying the returned set must not corrupt iteration expectations. Full and incremental report serialization is per datanode object, so canonical datanode resolution is critical. Tests should cover unknown WARN and DELETE modes, missing replica removal, new replica addition, pending allocation clearing, validator skip behavior, registration events, NodeNotFound handling, and full-report metrics success/failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManager.java

## Purpose
Defines the lower-level SCM container state manager contract. It owns container lifecycle state, container table persistence, in-memory replica sets, matching-container selection, and HA-replicated mutation entry points.

## Important APIs, Types, And Functions
Read APIs include `contains`, `getContainerIDs`, `getContainerInfos`, `getContainerCount`, `getContainer`, and `getContainerReplicas`. Replica APIs are `updateContainerReplica` and `removeContainerReplica`. Replicated mutations include `addContainer`, `updateContainerStateWithSequenceId`, `transitionDeletingOrDeletedToTargetState`, `removeContainer`, and `updateContainerInfo`. `updateDeleteTransactionId`, `getMatchingContainer`, and `reinitialize` round out the contract. `getType` identifies the HA request type as `SCMRatisProtocol.RequestType.CONTAINER`.

## Control Flow
The interface documents the lifecycle state machine: OPEN to CLOSING via FINALIZE, CLOSING to QUASI_CLOSED or CLOSED, QUASI_CLOSED to CLOSED, CLOSED or QUASI_CLOSED to DELETING, and DELETING to DELETED. Replicated methods must be idempotent, use protobuf arguments, and be suitable for SCM HA invocation.

## State And Persistence
The state manager is responsible for persistent `ContainerInfo` records and in-memory replica locations. The interface explicitly separates replicated persistent mutations from non-replicated report-derived replica updates.

## Dependencies And Integration Points
Extends `SCMHandler` and depends on `@Replicate`, container lifecycle protobufs, SCM Ratis request types, pipeline IDs, container table storage, and the state-machine exception type. It is the HA-facing backend for `ContainerManagerImpl`.

## Risks And Test Signals
Replicated mutation signatures are constrained by HA requirements; changing them can break Ratis invocation. The bypass transition from DELETING/DELETED back to CLOSED/QUASI_CLOSED is intentionally outside the normal state machine. Tests should cover lifecycle transition validity, idempotent repeated events, HA proxy invocation, table reinitialization, replica operations, and matching-container behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManagerImpl.java

## Purpose
Default `ContainerStateManager` implementation. It keeps container metadata in an in-memory `ContainerStateMap` backed by the SCM container table and transaction buffer, maintains report-derived replica sets, tracks round-robin container selection, and exposes HA-proxied replicated mutations.

## Important APIs, Types, And Functions
The private constructor initializes locks, state machine, configured container size, `ContainerStateMap`, `lastUsedMap`, transaction buffer, striped per-container locks, and pending-op hooks. `newStateMachine` defines lifecycle transitions and idempotent self-transitions. `initialize` loads all containers from the table and registers OPEN containers with existing pipelines. Mutators include `addContainer`, `updateContainerStateWithSequenceId`, `transitionDeletingOrDeletedToTargetState`, `updateContainerReplica`, `removeContainerReplica`, `updateDeleteTransactionId`, `removeContainer`, `reinitialize`, and `updateContainerInfo`. `getMatchingContainer` implements round-robin space selection.

## Control Flow
Startup iterates the table into memory, warning when OPEN containers reference missing or null pipelines. Adding a container buffers the table write, updates the in-memory map, and registers the container with the pipeline when possible; `ExecutionUtil` rollback removes partial state on failure. State updates synchronize sequence ID from the leader, compute the next lifecycle state, update map indexes, buffer the new table value, and run side effects such as removing finalized containers from pipelines. Matching starts after the last used ID, wraps to the head set, updates last-used time, and records the selected container.

## State And Persistence
Persistent state is `ContainerInfo` in `containerStore`, updated through `DBTransactionBuffer`. In-memory state includes `ContainerStateMap`, replica sets, `lastUsedMap`, and pipeline-container registrations. Replica add/remove completes pending replication/delete operations but does not write the container table. `updateContainerInfo` currently persists only the suppressed flag from the supplied proto onto the existing container.

## Dependencies And Integration Points
Depends on SCM config, `PipelineManager`, `DBTransactionBuffer`, `ContainerReplicaPendingOps`, `ContainerStateMap`, `StateMachine`, `ExecutionUtil`, Guava striped locks, SCM Ratis proxy invocation, and container table iterators. The builder wraps the implementation with `ContainerStateManagerInvoker` from `SCMRatisServer`.

## Risks And Test Signals
The class comment says calls are not thread safe, but the implementation uses global and striped locks; lock coverage and ordering are still important. Some rollback paths buffer or write old values and should be tested under injected failures. Pipeline registration for OPEN containers with missing metadata has special Recon behavior. Tests should cover table load, add rollback, idempotent transitions, sequence ID synchronization, FINALIZE pipeline removal, DELETING/DELETED resurrection bypass, pending-op completion on replica changes, matching-container wraparound, delete transaction persistence, and reinitialize.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerStateManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/IncrementalContainerReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/IncrementalContainerReportHandler.java

## Purpose
Processes incremental container reports from datanodes. It updates the datanode's container membership and the corresponding SCM replica/container state for only the reported changes.

## Important APIs, Types, And Functions
`IncrementalContainerReportHandler` extends `AbstractContainerReportHandler` and implements `EventHandler<IncrementalContainerReportFromDatanode>`. `getDatanodeDetails` resolves the canonical datanode from `NodeManager`. `processICR` synchronizes per datanode, updates `NodeManager` membership, validates replicas, delegates to `processContainerReplica`, clears pending allocations, and notifies report metrics.

## Control Flow
`onMessage` resolves the datanode and returns if unknown. `processICR` locks on the datanode to serialize with full reports, then loops through reported replica protos. In a `finally` block around container lookup, it removes node-manager membership for DELETED replicas and adds it for all others. Known containers are validated and processed. Exceptions are logged by category, including not-leader `SCMException`, and success is true if at least one replica is processed through the main try path.

## State And Persistence
Incremental reports update `NodeManager` membership, in-memory replica maps, pending allocation tracking, and possibly persistent container lifecycle/stats through shared abstract processing. It does not reconcile missing replicas; full reports own that path.

## Dependencies And Integration Points
Depends on heartbeat dispatcher ICR payloads, `NodeManager`, `ContainerManager`, `ContainerReportValidator`, `DatanodeInfo` pending allocation tracking, `SCMContext`, and shared report processing. It is the frequent lightweight update path complementing full reports.

## Risks And Test Signals
The membership update happens in a `finally` after container lookup, so unknown containers can still affect node-manager state based on replica state. Success metrics are coarse and may mark success after partial processing. Tests should cover DELETED membership removal, add membership for non-deleted replicas, validator failures, unknown container logging, SCM_NOT_LEADER handling, pending allocation clearing, serialization with FCR, and partial failure metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/IncrementalContainerReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/AbstractFindTargetGreedy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/AbstractFindTargetGreedy.java

## Purpose
Provides common greedy target-selection logic for container balancer strategies. It chooses an eligible target datanode for a candidate source/container while honoring placement policy, duplicate-replica avoidance, target ingress limits, and post-move utilization limits.

## Important APIs, Types, And Functions
Implements `FindTargetStrategy`. `findTargetForContainerMove` sorts targets through subclass `sortTargetForSource`, then tests each target. `containerMoveSatisfiesPlacementPolicy` validates the replica set after replacing the source with the target. `canSizeEnterTarget` enforces `maxSizeEnteringTarget` and upper utilization limit. `increaseSizeEntering` updates per-target scheduled ingress and reorders/removes targets. `reInitialize`, `resetTargets`, `getSizeEnteringNodes`, and `clearSizeEnteringNodes` manage per-iteration state.

## Control Flow
At iteration start, potential targets are loaded and each target's scheduled ingress starts at zero. For a candidate move, targets are sorted by the concrete strategy, existing replicas are rejected, placement is revalidated, and projected ingress/utilization is checked. After a move is scheduled, the target's scheduled ingress increases and the target is reinserted only if it remains below the ingress cap.

## State And Persistence
State is per-task, per-iteration memory: `sizeEnteringNode`, potential targets, configuration, upper limit, and dependencies. No persistence is performed.

## Dependencies And Integration Points
Depends on `ContainerManager`, `PlacementPolicyValidateProxy`, `NodeManager`, `DatanodeUsageInfo`, `ContainerReplica`, `ContainerInfo`, and `ContainerBalancerConfiguration`. Concrete subclasses provide usage-only or network-topology-aware sorting.

## Risks And Test Signals
`potentialTargets` is a collection supplied by subclasses and is mutated during balancing, so ordering and remove/add semantics matter. Missing `sizeEnteringNode` records cause warnings and reject moves. Tests should cover duplicate target replica rejection, placement-policy rejection, ingress cap, upper-limit projection, target reordering after ingress, missing container handling, and subclass sorting effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/AbstractFindTargetGreedy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancer.java

## Purpose
SCM service wrapper for the container balancer. It persists desired run state/configuration, starts and stops the asynchronous balancing task, reacts to leader and safe-mode status changes, validates configuration, and exposes status/metrics.

## Important APIs, Types, And Functions
`ContainerBalancer` extends `StatefulService<ContainerBalancerConfigurationProto>`. Important methods are `notifyStatusChanged`, `shouldRun`, `isBalancerRunning`, `getBalancerStatusInfo`, `start`, `startBalancer`, `stop`, `stopBalancer`, `saveConfiguration`, `validateConfiguration`, and `validateNodeList`. It owns `ContainerBalancerTask`, `ContainerBalancerConfiguration`, `ContainerBalancerMetrics`, the current balancing thread, a lock, and start time.

## Control Flow
On SCM status changes, the service stops if the SCM is no longer leader or enters safe mode, and starts if leader/out-of-safe-mode and persisted `shouldRun` is true. CLI/service start validates leader readiness and safe mode, reads persisted config, validates it, and starts a daemon `ContainerBalancerTask` with optional safe-mode-exit delay. Manual start saves config with `shouldRun=true`. Stop either stops the local task or persists `shouldRun=false` for an operator stop, then joins the task thread while repeatedly interrupting it.

## State And Persistence
Persistent service state is a `ContainerBalancerConfigurationProto` with `shouldRun` and `nextIterationIndex`, stored through `StatefulService`. Runtime state includes the active task, thread, metrics source, lock, start timestamp, and current config.

## Dependencies And Integration Points
Depends on `StorageContainerManager`, `SCMContext`, SCM service manager registration, stateful service state manager, Ozone configuration, DU refresh config, SCM node manager for include/exclude validation, and `ContainerBalancerTask`.

## Risks And Test Signals
Start/stop is lock-protected but thread join intentionally occurs outside the lock. Persisted config must be present for service auto-start; missing config means no run. Configuration validation enforces move timeout relationships and source/target size limits but only warns when balancing interval is shorter than DU refresh. Tests should cover leader/safe-mode transitions, persisted `shouldRun`, restart from next iteration, invalid node lists, invalid size and timeout configs, stop persistence, task thread lifecycle, and status proto conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerMetrics.java

## Purpose
Defines Hadoop Metrics2 counters for container balancer progress, latest-iteration results, cumulative move outcomes, unbalanced data size, and datanode involvement.

## Important APIs, Types, And Functions
`ContainerBalancerMetrics.create()` registers a Metrics2 source named `ContainerBalancerMetrics`. Counters include scheduled, completed, timeout, failed, data moved in bytes and GB, iteration count, datanodes involved, unbalanced GB, and unbalanced datanodes. Reset methods subtract current latest-iteration values. `incrementCurrentIterationContainerMoveMetric` maps `MoveManager.MoveResult` values to completed, timeout, or failed counters.

## Control Flow
The balancer task resets latest-iteration counters at the start of each iteration, increments scheduled counts when moves are submitted, increments result counters in move completion callbacks, and folds latest counters into cumulative counters at iteration end.

## State And Persistence
Metrics are process-local Hadoop Metrics2 mutable counters. They are not persisted across SCM restart. The `ms` field stores the metrics system reference but this class has no unregister method.

## Dependencies And Integration Points
Depends on Hadoop Metrics2 annotations, `DefaultMetricsSystem`, `MutableCounterLong`, and `MoveManager.MoveResult`. It is used by `ContainerBalancer` and `ContainerBalancerTask`, and status-info helper classes read its values.

## Risks And Test Signals
Using counters as resettable gauges by incrementing negative values requires accurate current values and can underflow if externally manipulated. GB and byte metrics are both tracked and can diverge if update order changes. Result classification must stay aligned with `MoveManager.MoveResult` enum additions. Tests should cover resets, cumulative folding, classification of completed/timeout/failure results, scheduled counters, and repeated metrics registration behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerSelectionCriteria.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerSelectionCriteria.java

## Purpose
Determines which containers on a candidate source datanode are eligible for balancing. It filters by include/exclude lists, prior selection, per-source leaving limits, per-iteration move-size limit, lifecycle/replica state, replication health, and in-flight replication/deletion.

## Important APIs, Types, And Functions
`getContainerIDSet` returns a cached, used-bytes-descending candidate set per datanode. `shouldBeExcluded` applies the main eligibility checks. `isContainerClosed` and `isContainerHealthyForMove` implement strict mode. `isContainerClosedRelaxed`, `hasMinClosedReplicas`, and `isContainerHealthyForMoveRelaxed` support `includeNonStandardContainers`. `addToExcludeDueToFailContainers` prevents repeated failures on a container. `getCandidateContainers` reads `NodeManager` membership and pre-filters configured include/exclude sets and already selected containers.

## Control Flow
For a source, candidates are fetched once and cached in a `TreeSet` ordered by largest used bytes first. Each balancing attempt calls `shouldBeExcluded`; excluded IDs are removed from the cached set by the task. Strict mode requires CLOSED container and CLOSED source replica plus HEALTHY replication state. Relaxed mode permits selected CLOSED/QUASI_CLOSED and OVER_REPLICATED cases with minimum closed replica and non-empty source-replica checks.

## State And Persistence
State is per-iteration memory: cached candidate sets, failed-container excludes, configured include/exclude sets, and selected container-to-source map references. It does not persist state.

## Dependencies And Integration Points
Depends on `NodeManager`, `ContainerManager`, `ReplicationManager`, `FindSourceStrategy`, container health results, protobuf lifecycle/replica states, and balancer configuration. It feeds `ContainerBalancerTask.matchSourceWithTarget`.

## Risks And Test Signals
`getCandidateContainers` mutates the set returned by `nodeManager.getContainers`; if that is not a defensive copy, configured filtering could affect node-manager state. The comparator returns 0 on missing container lookup, which can collapse distinct IDs in a `TreeSet`. Relaxed non-standard eligibility is subtle and must preserve replication safety. Tests should cover include-only mode, exclude lists, failed-container exclusion, selected-container exclusion, source leaving limit, per-iteration size limit, strict closed/healthy checks, relaxed over-replicated/quasi-closed cases, and NodeNotFound handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerSelectionCriteria.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerStatusInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerStatusInfo.java

## Purpose
Simple status DTO for exposing container balancer runtime status through protocol APIs.

## Important APIs, Types, And Functions
The class stores `startedAt`, a `ContainerBalancerConfigurationProto`, and a list of `ContainerBalancerTaskIterationStatusInfo`. Getters expose each field. `toProto` converts to `StorageContainerLocationProtocolProtos.ContainerBalancerStatusInfoProto`, encoding `startedAt` as epoch seconds and mapping iteration status objects through `toProto`.

## Control Flow
`ContainerBalancer.getBalancerStatusInfo` creates this object while the balancer is running. Protocol code calls `toProto` to serialize it for clients.

## State And Persistence
It is immutable runtime DTO state and has no persistence. The configuration embedded in it is a snapshot supplied by the balancer.

## Dependencies And Integration Points
Depends on protobuf types from `HddsProtos` and `StorageContainerLocationProtocolProtos`, Java time, and iteration status DTOs. It is the bridge from internal balancer task status to external SCM client protocol status.

## Risks And Test Signals
Epoch-second precision drops subsecond detail and omits timezone representation beyond the instant. Null inputs are not guarded. Tests should cover proto conversion, empty and non-empty iteration lists, started-at epoch value, and configuration passthrough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerStatusInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTask.java

## Purpose
Runs the container balancer loop. It classifies datanodes by utilization, selects source/target/container moves, schedules asynchronous moves, tracks per-iteration statistics and metrics, persists next-iteration progress, and stops when the cluster is balanced, configuration is exhausted, or SCM state becomes invalid.

## Important APIs, Types, And Functions
`ContainerBalancerTask` implements `Runnable`. Key methods are `run`, `stop`, `balance`, `initializeIteration`, `doIteration`, `matchSourceWithTarget`, `processMoveSelection`, `moveContainer`, `checkIterationMoveResults`, `cancelMovesThatExceedTimeoutDuration`, `updateTargetsAndSelectionCriteria`, `incSizeSelectedForMoving`, `resetState`, `calculateAvgUtilization`, and `getCurrentIterationsStatistic`. It uses `FindSourceGreedy`, `FindTargetGreedyByUsageInfo` or `FindTargetGreedyByNetworkTopology`, `ContainerBalancerSelectionCriteria`, `MoveManager`, and `ContainerBalancerMetrics`. Enums `IterationResult` and `Status` represent loop and task state.

## Control Flow
`run` optionally sleeps after safe-mode exit, calls `balance`, and marks STOPPED in `finally`. `balance` loops from persisted `nextIterationIndex` through configured iterations, resets state, optionally triggers datanode DU refresh and waits for node reports, initializes over/under-utilized sets, executes an iteration, records status info, clears strategy traffic maps, increments iteration metrics, persists next iteration on success, sleeps between iterations, and stops with persisted `shouldRun=false` when complete or no longer balanceable. `doIteration` repeatedly checks move-size and datanode-involvement limits, adapts candidate sets near limits, gets a source, finds a target/container, and schedules the move. Move futures update metrics and actual bytes moved; iteration end waits for all futures or cancels timed-out moves.

## State And Persistence
Runtime state includes utilization lists, selected source/target sets, container source/target maps, scheduled and actual byte counts, move futures, current iteration start time, status queue, and strategy traffic maps. Persistent state is only through `ContainerBalancer.saveConfiguration`, which stores `shouldRun` and next iteration index. Actual container movement state is owned by `MoveManager`, replication manager, datanodes, and container reports.

## Dependencies And Integration Points
Depends on `StorageContainerManager`, `NodeManager`, `ContainerManager`, `ReplicationManager`, `MoveManager`, placement validation, network topology, SCM leader/safe-mode context, Ozone and HDDS timing config, balancer config, datanode usage info, and status DTO classes. It is the main orchestration point connecting SCM utilization observations to replication-manager move operations.

## Risks And Test Signals
`sizeActuallyMovedInLatestIteration` is updated from async callbacks without synchronization. Moves are treated optimistically for scheduling when futures are still running, so later failures can leave selection accounting more conservative than actual movement. Datanode-involvement adaptation depends on integer truncation of ratio times cluster size. `withinThresholdUtilizedNodes` is populated but not used as candidates. Tests should cover average utilization, include/exclude node filtering, safe-mode/leader invalidation, DU-trigger wait interruption, over/under threshold classification, candidate adaptation at limits, duplicate container prevention, move-result metric classification, timeout cancellation, persisted next iteration, stop behavior, and current-iteration status generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTask.java -->

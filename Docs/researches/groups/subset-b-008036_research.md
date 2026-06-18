# subset-b-008036 research

This grouped report covers SCM node and pipeline management files from Apache Ozone. Each section preserves the source path in its title and is wrapped for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeManager.java

## Purpose
`SCMNodeManager` is the Storage Container Manager side implementation of `NodeManager`. It owns datanode registration, heartbeat command dispatch, node reports, node operational state synchronization, topology registration, storage and usage summaries, pipeline/container membership delegation, and JMX/metrics-facing views of the cluster. It coordinates the lower-level `NodeStateManager`, in-memory command queues, `PendingContainerTracker`, SCM layout-version finalization, and event publication.

## Important APIs, Types, And Functions
The constructor wires `NodeStateManager`, `CommandQueue`, `SCMNodeMetrics`, `PendingContainerTracker`, `NetworkTopology`, SCM HA context, layout version manager, configuration-derived pipeline/container limits, and non-writable-node filtering. `register` validates datanode software layout version, resolves current RPC address, inserts or updates the datanode in the topology and state manager, updates hostname/IP reverse indexes, processes the initial node report, and emits `NEW_NODE` or `NODE_ADDRESS_UPDATE`.

Heartbeat handling is centered on `processHeartbeat`, which updates last heartbeat, metrics, operational-state reconciliation, drains queued commands, invokes optional send-command callbacks, and folds datanode command queue reports into `DatanodeInfo`. Layout and finalization handling flows through `processLayoutVersionReport` and `sendFinalizeToDatanodeIfNeeded`, with leader-only `FinalizeNewLayoutVersionCommand` publication. Query APIs expose node counts, status, all nodes, storage stats, usage info, peer lists, pipeline/container memberships, command counts, and last heartbeat.

Operational-state APIs include `setNodeOperationalState`, `updateDatanodeOpState`, `opStateDiffers`, and `maybeNotifyReplicationManager`. Storage aggregation APIs include `getStats`, `getNodeStats`, `getNodeStat`, `getNodeInfo`, `getNodeStatusInfo`, `getNodeStatistics`, `calculateStorageCapacity`, `calculateStoragePercentage`, `getTotalReserved`, and `getTotalFilesystemUsage`. Pipeline/container integration passes through `addPipeline`, `removePipeline`, `getPipelines`, `addContainer`, `removeContainer`, and `getContainers`.

## Control Flow
Registration first rejects incompatible datanode software layout versions. It updates IP/hostname from `Server.getRemoteIp` when inside RPC, computes network identity/location, and either adds a new node or refreshes an existing node if address or version changed. New nodes are inserted into `NetworkTopology` before `NodeStateManager`, then the code verifies that topology parent assignment is present. Existing-node address changes update the DNS-to-datanode map, topology, state manager, report data, and fire the address-update event.

Heartbeats update liveness before acquiring the manager write lock for command queue mutation. Leader SCMs treat SCM node state as authoritative: if a heartbeat reports a different persisted operational state, SCM queues `SetNodeOperationalStateCommand` with the leader term. Followers instead update their local view from the heartbeat. After that, the stored `DatanodeDetails` persisted operational fields are refreshed and replication manager is notified on relevant transitions.

JMX and metrics flows build snapshots, not linearizable views. Node counts are grouped by operational and health state; storage summaries skip dead in-service nodes for usage-state aggregation and withhold raw filesystem totals if any live report lacks filesystem fields. Non-writable nodes are detected by health/operational writability plus Ratis volume/container space checks. Removal requires a node to be decommissioned or dead, removes it from topology and node maps, clears reverse address indexes, and drains pending commands.

## State And Persistence Behavior
Most state here is in-memory and delegated. `NodeStateManager` owns node lifecycle state; `CommandQueue` owns per-datanode commands; `dnsToDnIdMap` maps host/IP strings to one or more `DatanodeID`s; `PendingContainerTracker` tracks optimistic container allocation reservations. `SCMNodeManager` also registers an MBean and a Hadoop metrics source that must be unregistered on close.

Persistent behavior is indirect. Node operational state is persisted by datanodes and reconciled via heartbeats; SCM sends update commands when leader state differs. Layout finalization commands cause datanodes to update their metadata layout version. Node and pipeline/container membership changes affect SCM state stores through collaborators such as `NodeStateManager` and `PipelineStateManager`, not direct DB writes in this class.

The class uses a `ReentrantReadWriteLock` around command queue and some removal operations, while `NodeStateManager` and concurrent maps provide their own synchronization. Returned lists and maps are intentionally snapshots and may be stale immediately after creation.

## Dependencies And Integration Points
The class integrates with SCM event bus events including `NEW_NODE`, `NODE_ADDRESS_UPDATE`, `DATANODE_COMMAND`, `DATANODE_COMMAND_COUNT_UPDATED`, and `REPLICATION_MANAGER_NOTIFY`. It depends on `NetworkTopology` for rack placement, `SCMContext` for leader/term/safemode behavior, `HDDSLayoutVersionManager` and `FinalizationManager` for upgrades, protobuf reports from datanodes, `PipelineManager` through the SCM context for peer calculation, and Hadoop metrics/JMX.

It is consumed by datanode RPC handlers, pipeline placement, replication manager, container manager, admin/decommission flows, dashboards, and metrics scrapers. `NonWritableNodeFilter` shares placement semantics by using `SCMCommonPlacementPolicy.hasEnoughSpace` plus committed-space fallback.

## Risks And Edge Cases
The registration path has several race-sensitive side effects: topology, state map, DNS reverse index, and node reports must remain consistent when IP/hostname changes. If `getNodesByAddress` maps a removed ID to `null`, callers must tolerate nullable entries because it maps through `getNode`. `calculateStoragePercentage` divides by capacity without a zero-capacity guard, so bad reports can produce invalid percentages.

Snapshot methods should not be used for strict invariants. Nested read locks call other methods that acquire the same read lock, which is safe with `ReentrantReadWriteLock` but should be considered when changing locking. `removeNode` calls `getCommandQueue` while already holding the write lock; this relies on reentrant write locks. Leader-only command publication must handle `NotLeaderException` because leadership can change between checks and term retrieval.

## Test Signals
High-value tests include registration of new and existing nodes, address/hostname update and DNS index cleanup, topology parent assignment, heartbeat command drain and command-count report merging, leader-vs-follower operational-state reconciliation, layout finalization command emission, node report storage aggregation, non-writable-node metrics, pending allocation rollback, and removal preconditions. Concurrency tests should exercise command queue locking, stale snapshot behavior, and address updates racing with lookups.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeMetrics.java

## Purpose
`SCMNodeMetrics` is the Hadoop metrics source for SCM node manager counters and gauges. It exposes heartbeat/report processing counters, pending-container allocation counters, and dynamic gauges derived from `NodeManagerMXBean`.

## Important APIs, Types, And Functions
`create` registers the metrics source under `SCMNodeMetrics` in `DefaultMetricsSystem`; `unRegister` removes it. Package-private incrementers update heartbeat, node-report, command-queue-report, pending-container, and skipped-full-node-allocation counters. `getMetrics` builds node-state cross-product gauges, all-node count, non-writable and volume-failure gauges, and storage capacity/usage gauges. `diskMetricDescription` creates human-readable descriptions for generated storage metrics.

## Control Flow
Metrics snapshots call back into the supplied `NodeManagerMXBean` for current `getNodeCount`, `getNodeInfo`, and `getNodeStatistics` maps. For each operational/health combination it camelizes a gauge name and increments an aggregate `AllNodes` gauge. Optional map keys such as `NonWritableNodes` and `VolumeFailures` are checked before adding gauges. Remaining storage entries are emitted with descriptions inferred from their names.

## State And Persistence Behavior
The class keeps Hadoop `MutableCounterLong` counters in memory. Gauges are not stored; they are recomputed on collection. Registration state lives in the process metrics system and must be explicitly unregistered to prevent duplicate sources in tests or restarted services.

## Dependencies And Integration Points
It depends on Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, `Interns`, and the `NodeManagerMXBean` contract. `SCMNodeManager` creates and updates it, and observability systems scrape the generated metrics.

## Risks And Edge Cases
Gauge names are generated from map keys, so changing `SCMNodeManager` labels can break dashboards. `getMetrics` parses `NonWritableNodes` and `VolumeFailures` from strings, so malformed values from the MXBean would throw during metrics collection. Missing optional keys are tolerated. The `textMetric` field appears test-like and not functionally important.

## Test Signals
Tests should verify metrics registration/unregistration, counter increments, generated cross-product gauges for all node states, storage gauge description mapping, and behavior when optional node-statistics keys are absent or present.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeStorageStatMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeStorageStatMXBean.java

## Purpose
`SCMNodeStorageStatMXBean` defines the JMX management contract for per-datanode and aggregate storage capacity, remaining, used, and volume details.

## Important APIs, Types, And Functions
The interface exposes `getCapacity`, `getRemainingSpace`, `getUsedSpace`, `getTotalCapacity`, `getTotalSpaceUsed`, `getTotalFreeSpace`, and `getStorageVolumes`. Per-node methods use `UUID` datanode IDs and volume details are returned as `Set<StorageLocationReport>`.

## Control Flow
There is no implementation control flow in this file. Implementations are expected to look up a datanode ID, aggregate over its storage reports, and expose totals through JMX.

## State And Persistence Behavior
The interface owns no state. Implementations may back it with in-memory reports derived from datanode node reports, as `SCMNodeStorageStatMap` does.

## Dependencies And Integration Points
It depends on `StorageLocationReport` from the Ozone container common package and Hadoop interface-audience annotations. JMX consumers and SCM storage-stat implementations use this contract.

## Risks And Edge Cases
The contract does not define behavior for unknown datanode IDs, null IDs, empty reports, or whether returned volume sets are defensive copies. Implementers need to document and guard those behaviors.

## Test Signals
Implementation tests should assert per-node and aggregate values, unknown-node behavior, and mutation safety of returned `StorageLocationReport` sets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeStorageStatMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeStorageStatMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeStorageStatMap.java

## Purpose
`SCMNodeStorageStatMap` maintains storage-location reports per datanode and classifies node reports by utilization and failed-volume conditions. It implements `SCMNodeStorageStatMXBean` for storage JMX views.

## Important APIs, Types, And Functions
The constructor reads warning and critical utilization thresholds. `isKnownDatanode`, `insertNewDatanode`, `updateDatanodeMap`, and `removeDatanode` manage the `UUID -> Set<StorageLocationReport>` map. `processNodeReport` converts protobuf storage reports, tracks failed and critically full volumes, updates the map, logs threshold warnings, and returns `StorageReportResult`. JMX methods aggregate capacity, remaining, and used space per node or cluster-wide. `getDatanodeList` filters datanodes by `UtilizationThreshold`, and `getScmUsedratio` truncates utilization to four decimal places.

## Control Flow
Processing a node report iterates each storage report, converts it to a `StorageLocationReport`, adds failed volumes to one set, adds critically utilized nonfailed volumes to another, and accumulates total capacity, remaining, and SCM-used bytes. It inserts or replaces the datanode's report set, then prioritizes status as datanode out-of-space if aggregate utilization is critical. Otherwise it logs warning threshold crossings and returns one of all-well, storage-out-of-space, failed-storage, or combined failure statuses based on the volume sets.

## State And Persistence Behavior
State is a `ConcurrentHashMap<UUID, Set<StorageLocationReport>>`, with synchronized blocks around insert/update/remove despite the concurrent map. There is no durable persistence; the map is rebuilt from datanode reports. Returned sets are direct map values, not defensive copies, so callers can observe and potentially mutate internal state if they retain references.

## Dependencies And Integration Points
The class depends on Ozone configuration keys for thresholds, protobuf `NodeReportProto` and `StorageReportProto`, `StorageLocationReport`, and `SCMException` result codes. It is an older storage-report processing and JMX component adjacent to the newer `DatanodeInfo` storage report handling in `SCMNodeManager`.

## Risks And Edge Cases
`getCapacity`, `getRemainingSpace`, and `getUsedSpace` assume the datanode ID is present; unknown IDs cause null iteration failures rather than clean exceptions. `getScmUsedratio` divides by capacity, so zero-capacity reports are risky. `putIfAbsent` is redundant inside synchronization. The local variable `storagReportSet` is misspelled but harmless. Directly returning internal volume sets can corrupt future aggregates.

## Test Signals
Tests should cover first report insert, report update, duplicate and missing datanode exceptions, warning/critical thresholds, failed and full volume combinations, zero/invalid capacity handling, aggregate totals, datanode list filtering by utilization threshold, and mutation safety of returned storage-volume sets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeStorageStatMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StaleNodeHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StaleNodeHandler.java

## Purpose
`StaleNodeHandler` reacts to a datanode entering stale health state by closing/finalizing all pipelines that include that datanode.

## Important APIs, Types, And Functions
It implements `EventHandler<DatanodeDetails>`. The constructor receives `NodeManager` and `PipelineManager`. `onMessage` fetches pipeline IDs from `nodeManager.getPipelines(datanodeDetails)` and calls `pipelineManager.closePipeline` for each.

## Control Flow
On an event, it logs the stale transition and the affected pipeline set. It iterates the set and attempts to close each pipeline independently. `IOException` from any close is logged and does not stop processing of other pipelines.

## State And Persistence Behavior
The handler owns no state beyond collaborator references. Persistent effects are delegated to `PipelineManager.closePipeline`, which may update pipeline/container state and emit close-container events through its implementation.

## Dependencies And Integration Points
It is wired into SCM's event queue for stale-node events. It depends on `NodeManager` membership tracking and `PipelineManager` lifecycle transitions.

## Risks And Edge Cases
The pipeline set is a snapshot; pipelines added or removed concurrently may not be represented. Exceptions are logged at info level without retry. Closing a pipeline can have broad side effects, including container finalization, so stale detection thresholds affect write availability.

## Test Signals
Tests should verify all pipelines for a stale node are closed, failures on one pipeline do not skip subsequent pipelines, and empty pipeline sets are harmless.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StaleNodeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StartDatanodeAdminHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StartDatanodeAdminHandler.java

## Purpose
`StartDatanodeAdminHandler` reacts when a datanode begins an admin workflow, such as decommission or maintenance, by closing all pipelines that include that datanode.

## Important APIs, Types, And Functions
It implements `EventHandler<DatanodeDetails>`. `onMessage` asks `NodeManager` for the datanode's pipelines and calls `PipelineManager.closePipeline` for each.

## Control Flow
The flow mirrors `StaleNodeHandler`: log the admin-start event, iterate the pipeline IDs, attempt close, and log any `IOException` without failing the event handler loop.

## State And Persistence Behavior
The handler has no internal mutable state. It delegates state changes to the pipeline manager, which persists pipeline state transitions through SCM HA/Ratis and the pipeline store in the implementation.

## Dependencies And Integration Points
It integrates with SCM's admin/decommission/maintenance event path. It depends on node-to-pipeline membership being current enough to close write paths before admin operations proceed.

## Risks And Edge Cases
Snapshot pipeline membership can miss concurrent additions. Failure to close a pipeline only logs, so callers need separate admin workflow checks to ensure pipeline drain actually completed. The handler closes all pipelines regardless of whether they are already closing or closed; idempotence depends on `PipelineManager`.

## Test Signals
Tests should cover decommission/maintenance start events, multiple pipeline closure, empty memberships, and IOException handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StartDatanodeAdminHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StorageReportResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StorageReportResult.java

## Purpose
`StorageReportResult` is a small value object returned by storage-report processing to describe aggregate report status and sets of full or failed volumes.

## Important APIs, Types, And Functions
The object stores an `SCMNodeStorageStatMap.ReportStatus`, a set of full `StorageLocationReport`s, and a set of failed `StorageLocationReport`s. Getters expose those fields. The nested package-private `ReportResultBuilder` supports fluent `setStatus`, `setFullVolumeSet`, `setFailedVolumeSet`, and `build`.

## Control Flow
There is no business control flow beyond builder construction. `SCMNodeStorageStatMap.processNodeReport` chooses a status and optional sets, then builds this result.

## State And Persistence Behavior
Instances hold references to the provided sets and do not defensively copy them. There is no persistence and no immutability enforcement; fields are private but not final.

## Dependencies And Integration Points
The class depends on `SCMNodeStorageStatMap.ReportStatus` and `StorageLocationReport`. It is part of the storage-report classification pathway.

## Risks And Edge Cases
Builder fields can be left null. Consumers must handle null full or failed volume sets for statuses that do not set them. Since sets are not copied, later caller mutation can alter the observed result.

## Test Signals
Tests should verify each status combination from `SCMNodeStorageStatMap`, null behavior for omitted sets, and whether callers require defensive copies or null-safe access.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StorageReportResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/package-info.java

## Purpose
This package descriptor documents the SCM node-management package: registration, removal, heartbeat handling, node statistics, and container-manager queries of datanode state.

## Important APIs, Types, And Functions
There are no executable APIs. The text describes the package role around node manager responsibilities and statistics exchanged through heartbeats.

## Control Flow
Not applicable. It is Java package documentation only.

## State And Persistence Behavior
No state is defined. It frames the state owned by package classes such as `SCMNodeManager`, `NodeStateManager`, and related state maps.

## Dependencies And Integration Points
The package integrates SCM datanode management with container manager and heartbeat/report processing components.

## Risks And Edge Cases
Documentation can drift as node manager responsibilities change, especially around admin state, HA leadership, and layout finalization, which are now significant parts of the package behavior.

## Test Signals
No direct tests are needed. Documentation should be reviewed when node management workflows are changed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/DatanodeEntry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/DatanodeEntry.java

## Purpose
`DatanodeEntry` is the `NodeStateMap` value object pairing a `DatanodeInfo` with the set of container IDs currently associated with that datanode.

## Important APIs, Types, And Functions
It stores `DatanodeInfo info` and a `TreeSet<ContainerID> containers`. Methods expose `getInfo`, `getContainerCount`, `copyContainers`, `add`, `remove`, and test-only `setContainersForTesting`.

## Control Flow
The class only mutates its set when called by `NodeStateMap`, which provides external locking. `copyContainers` returns a new `TreeSet`, preserving sorted container order and avoiding direct set mutation by callers.

## State And Persistence Behavior
State is in-memory only. The container set is not persisted here; SCM rebuilds or updates it via reports and container event handling around the broader node state manager.

## Dependencies And Integration Points
It depends on `DatanodeInfo` and `ContainerID` and is package-private for construction by `NodeStateMap`. It is not a public node-management API.

## Risks And Edge Cases
The internal set is not synchronized by itself, so it relies on `NodeStateMap` lock discipline. `updateNode` in `NodeStateMap` replaces the entire entry and therefore can discard existing container membership if used without migration.

## Test Signals
Tests should validate sorted copy behavior, add/remove idempotence, and preservation or intentional replacement of container membership during node updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/DatanodeEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/Node2PipelineMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/Node2PipelineMap.java

## Purpose
`Node2PipelineMap` maintains the in-memory reverse index from datanode ID to pipeline IDs containing that datanode.

## Important APIs, Types, And Functions
`getPipelines` returns a defensive `HashSet` snapshot or an empty set. `getPipelinesCount` returns its size. `addPipeline` adds the pipeline ID to every node in a pipeline. `removePipeline` removes it from each node's set.

## Control Flow
The map is updated when pipeline allocation or removal happens. It uses `ConcurrentHashMap` and concurrent key sets, so add/remove can run without a global lock. Removing a pipeline leaves an empty set in the map rather than removing the datanode key.

## State And Persistence Behavior
State is memory-only. The source comment notes it should be regenerated from pipeline reports on SCM restart. In current integration, `PipelineStateManagerImpl.initialize` repopulates node pipeline membership from the persisted pipeline store.

## Dependencies And Integration Points
The map depends on `DatanodeID`, `DatanodeDetails`, `Pipeline`, and `PipelineID`. It is used by node state management and queried by handlers such as stale/admin node pipeline closers and placement policy pipeline-count logic.

## Risks And Edge Cases
Empty sets remain after removal, which is not functionally wrong but can retain keys. If pipeline membership changes without corresponding add/remove calls, the reverse index becomes stale and can cause missed close operations or incorrect placement limits. Returned sets are snapshots, so concurrent updates are not reflected.

## Test Signals
Tests should cover add/remove for multi-node pipelines, defensive copy behavior, no-pipeline empty result, count after removal, and restart reconstruction from persisted pipelines.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/Node2PipelineMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeAlreadyExistsException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeAlreadyExistsException.java

## Purpose
`NodeAlreadyExistsException` signals that a datanode with the same `DatanodeID` already exists in `NodeStateMap`.

## Important APIs, Types, And Functions
It extends `NodeException` and provides a no-argument constructor plus a `DatanodeID` constructor that formats a useful message.

## Control Flow
`NodeStateMap.addNode` throws it when the ID key is already present. Callers such as `SCMNodeManager.register` catch it as a benign duplicate-registration path.

## State And Persistence Behavior
The exception carries only a message. It has no persistent behavior.

## Dependencies And Integration Points
It depends on `DatanodeID` and the node state map exception hierarchy. It is part of the checked-exception contract for node insertion.

## Risks And Edge Cases
The no-argument constructor yields a null message, which is less useful in logs. Duplicate registration may be benign or a symptom depending on caller context, so catch sites should preserve enough context.

## Test Signals
Tests should verify duplicate add throws this type and message-bearing construction includes the datanode ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeAlreadyExistsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeException.java

## Purpose
`NodeException` is the checked base class for node-state-map errors.

## Important APIs, Types, And Functions
It extends `Exception` and provides no-argument and message constructors.

## Control Flow
Subclasses such as `NodeAlreadyExistsException` and `NodeNotFoundException` are thrown by node state map operations and propagated through `NodeManager` APIs.

## State And Persistence Behavior
The class carries only exception message/cause state inherited from `Exception`. It has no persistence.

## Dependencies And Integration Points
It defines the common exception hierarchy for `org.apache.hadoop.hdds.scm.node.states`.

## Risks And Edge Cases
There is no cause-taking constructor, so wrapping lower-level exceptions would lose direct causal chains unless subclasses are extended.

## Test Signals
Direct tests are low value. API tests should assert callers handle the concrete checked subclasses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeNotFoundException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeNotFoundException.java

## Purpose
`NodeNotFoundException` signals that a requested datanode ID is absent from `NodeStateMap`.

## Important APIs, Types, And Functions
It extends `NodeException` and has no-argument and `DatanodeID` constructors. The ID constructor formats `Datanode <id> not found`.

## Control Flow
`NodeStateMap.getExisting` throws it, and many read/update/remove operations propagate it. Higher-level managers either surface it, translate it into warnings, or treat it as a stale report.

## State And Persistence Behavior
The exception is transient and contains only message state.

## Dependencies And Integration Points
It depends on `DatanodeID` and appears throughout `SCMNodeManager`, placement providers, and report handlers where node membership is looked up.

## Risks And Edge Cases
Some higher-level methods convert not-found to null or logs, while others propagate it. Callers need to know whether absence is exceptional, a stale heartbeat/report, or expected during concurrent removal.

## Test Signals
Tests should verify missing node paths in `NodeStateMap`, `SCMNodeManager` report handling, EC read-pipeline creation, and removal race handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeNotFoundException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeStateMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeStateMap.java

## Purpose
`NodeStateMap` is the thread-safe in-memory map from `DatanodeID` to `DatanodeEntry`, providing node details, status filters, and per-node container membership.

## Important APIs, Types, And Functions
Mutation methods include `addNode`, `removeNode`, `updateNode`, `updateNodeHealthState`, `updateNodeOperationalState`, `addContainer`, `removeContainer`, and `setContainersForTesting`. Read methods include `getNodeInfo`, `getNodeStatus`, `getAllDatanodeInfos`, `getDatanodeDetails`, `getDatanodeInfos`, `getNodeCount`, `getTotalNodeCount`, `getContainers`, and `getContainerCount`. Private helpers `getExisting`, `countNodes`, `filterNodes`, and `matching` centralize locking and predicates.

## Control Flow
All public methods acquire a read or write lock around `nodeMap`. Add rejects duplicate IDs. Update replaces the `DatanodeEntry` for an ID and returns the previous `DatanodeInfo`. Health and operational-state updates mutate the `NodeStatus` inside the existing `DatanodeInfo`. Filtering APIs construct predicate chains for exact `NodeStatus`, operational state, health state, or wildcards.

Container operations delegate to the entry's `TreeSet`. Reads return copies for container sets and collected lists for node sets, so callers receive snapshots. `toString` intentionally reports only total node count and warns that no global consistency is guaranteed.

## State And Persistence Behavior
State is an in-memory `HashMap` protected by a `ReentrantReadWriteLock`. The class does not persist to disk; higher layers rebuild or update it from registration, heartbeat, container report, and pipeline/container events. `DatanodeInfo` objects are returned directly, so object-level mutation can occur outside `NodeStateMap` unless callers respect ownership.

## Dependencies And Integration Points
It depends on `DatanodeInfo`, `NodeStatus`, protobuf node state enums, `DatanodeID`, and `ContainerID`. It is used by `NodeStateManager`, which wraps this low-level map with heartbeat health checking and SCM events.

## Risks And Edge Cases
`updateNode` replaces the full `DatanodeEntry`, dropping existing container membership. That is safe only if callers intentionally rebuild membership or do not care about the old container set. Directly returning `DatanodeInfo` means the map lock does not protect later mutations to that object. Predicate filtering uses snapshots under lock but results can be stale immediately after return.

## Test Signals
Tests should cover duplicate add, missing-node exceptions, node update semantics including container membership replacement, status transitions, wildcard filtering counts, returned container copy isolation, concurrent read/write behavior, and removal followed by lookup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeStateMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/ReportResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/ReportResult.java

## Purpose
`ReportResult<T>` is a generic immutable-style result describing reconciliation between a datanode report and SCM's node-to-object mappings, such as missing and newly discovered containers or pipelines.

## Important APIs, Types, And Functions
It stores `ReportStatus`, `missingEntries`, and `newEntries`. Getters expose those fields. `ReportResultBuilder<T>` sets status, missing entries, and new entries, defaulting omitted sets to `Collections.emptySet()` during `build`. `ReportStatus` covers all-well, missing, new, combined missing/new, and new-datanode cases.

## Control Flow
The builder normalizes null missing/new sets to empty sets before constructing the result. The private constructor enforces non-null sets with `Objects.requireNonNull`.

## State And Persistence Behavior
The class holds references to the sets passed to the builder or singleton empty sets. It has no durable persistence. Fields are private but not final, though there are no setters on the built object.

## Dependencies And Integration Points
It is generic and only depends on Java collections. It is intended for node report reconciliation components that compare SCM state with datanode-reported state.

## Risks And Edge Cases
The builder does not require a status, so a result with null status is possible. Provided sets are not defensively copied, so external mutation can alter the result. Consumers must interpret `NEW_DATANODE_FOUND` separately from normal new-entry reconciliation.

## Test Signals
Tests should verify null-set normalization, status coverage, set preservation, and caller behavior for missing status or externally mutated input sets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/ReportResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/package-info.java

## Purpose
This package descriptor labels `org.apache.hadoop.hdds.scm.node.states` as the node-state package.

## Important APIs, Types, And Functions
There are no executable APIs. The surrounding package contains state maps, node entries, report reconciliation results, and node-specific exceptions.

## Control Flow
Not applicable.

## State And Persistence Behavior
No state is defined in this file. Package classes mostly maintain in-memory state that higher layers rebuild or persist indirectly.

## Dependencies And Integration Points
The package is used by node management and pipeline placement components for node state lookup and reverse indexes.

## Risks And Edge Cases
The descriptor is minimal and may not communicate important locking and snapshot semantics present in the package.

## Test Signals
No direct tests are needed; update documentation if package responsibilities expand.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/package-info.java

## Purpose
This package descriptor identifies the SCM package as containing StorageContainerManager classes.

## Important APIs, Types, And Functions
There are no executable APIs. The package includes SCM placement, node, pipeline, container, safemode, protocol, server, and security components.

## Control Flow
Not applicable.

## State And Persistence Behavior
No state is defined in this file.

## Dependencies And Integration Points
It provides top-level Java package documentation for the server-side SCM module.

## Risks And Edge Cases
The documentation is broad and sparse; it may not help readers navigate major SCM subsystems.

## Test Signals
No direct tests are needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/BackgroundPipelineCreator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/BackgroundPipelineCreator.java

## Purpose
`BackgroundPipelineCreator` is an `SCMService` that periodically or reactively creates new pipelines when SCM leadership, safemode, and precheck conditions allow it.

## Important APIs, Types, And Functions
The constructor reads safemode pipeline-creation policy, post-safemode wait time, creation interval, and derives the leader-specific thread name. `start` creates a daemon-like named worker thread with an uncaught exception handler that shuts down SCM. `stop` interrupts and joins that thread. `run` loops while running, calling `shouldRun` and `createPipelines`. `notifyStatusChanged`, `notifyEventTriggered`, and `shouldRun` implement the `SCMService` contract. `createPipelines` builds replication configs from cluster defaults and asks `PipelineManager` to create pipelines until creation fails for each config.

## Control Flow
The service starts in `PAUSING`. `notifyStatusChanged` transitions to `RUNNING` only when SCM is leader-ready and either out of safemode or configured to create pipelines in safemode. Normal periodic execution waits until the post-safemode delay has elapsed. Certain events, including new node, node address update, unhealthy-to-healthy node, and precheck completion, set a one-shot flag and notify the monitor so creation can run immediately.

Pipeline creation chooses the configured default replication type. For non-EC types it iterates all nonzero replication factors; for EC default it still creates only Ratis factor-one support pipelines. Unsupported or disabled combinations are skipped. A looping iterator repeatedly tries configs and removes a config when creation throws, ending when all current configs fail.

## State And Persistence Behavior
The class owns thread lifecycle state, service status, one-shot trigger state, and timing fields. It does not persist pipeline records directly; successful creation is delegated to `PipelineManager`, which persists via `PipelineStateManager`. Thread state is protected by `AtomicBoolean`, a `ReentrantLock`, and a monitor object.

## Dependencies And Integration Points
It depends on SCM HA service events, `SCMContext` leadership/safemode/precheck state, `PipelineManager`, replication config helpers, and Ozone/HDDS config keys. `PipelineManagerImpl.newPipelineManager` creates and registers it with `SCMServiceManager`.

## Risks And Edge Cases
The creation loop can aggressively create pipelines until every config fails; placement failure is used as the stopping condition. If unexpected exceptions repeat, they are logged and the config is removed for that run, not retried until the next run. Interruption during monitor wait stops the service by setting `running` false. One-shot runs bypass post-safemode delay, so event sources must be intentional.

## Test Signals
Tests should validate service state transitions, one-shot event triggers, safemode creation settings, delayed post-safemode execution, start/stop idempotence, exception handling in creation loops, replication config selection for RATIS/STAND_ALONE/EC defaults, and SCM shutdown on uncaught worker errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/BackgroundPipelineCreator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/ECPipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/ECPipelineProvider.java

## Purpose
`ECPipelineProvider` creates EC pipelines and read pipelines for EC containers. It assigns EC replica indexes to selected datanodes and sorts read pipelines by node health.

## Important APIs, Types, And Functions
It extends `PipelineProvider<ECReplicationConfig>`. `create(replicationConfig)` delegates with empty excluded/favored lists. The placement-aware `create` asks an EC placement policy for `replicationConfig.getRequiredNodes()` datanodes with configured container size. The node-list `create` assigns replica indexes starting at 1. `createForRead` builds a datanode-to-replica-index map from replicas, skips dead or unknown nodes, sorts by `CREATE_FOR_READ_COMPARATOR`, and creates an allocated pipeline. `close` is a no-op.

## Control Flow
Write pipeline creation is placement-policy driven. Read pipeline creation iterates current replicas, consults `NodeManager.getNodeStatus`, filters out dead nodes and missing nodes, records indexes from `ContainerReplica`, sorts healthier nodes first and dead last by comparator, then builds a pipeline with the original replica-index map.

## State And Persistence Behavior
The provider is stateless aside from references to configuration, node manager, state manager, placement policy, and container size. It creates `Pipeline` objects in `ALLOCATED` state; persistence occurs only when the pipeline manager adds them.

## Dependencies And Integration Points
It depends on `ECReplicationConfig`, `PlacementPolicy`, `NodeManager`, `NodeStatus`, `ContainerReplica`, and `PipelineStateManager`. `PipelineFactory` owns the EC provider.

## Risks And Edge Cases
`createForRead` can return fewer nodes than the EC config requires if replicas are missing, unknown, or dead; that may be valid for degraded reads but needs callers to understand it. Sorting uses node status map lookups and assumes all DNS in the list have entries. `close` is empty because EC datanodes do not need the same close command semantics as Ratis pipelines, so lifecycle changes rely on SCM state and container handling.

## Test Signals
Tests should verify EC write placement size and index assignment, excluded/favored node propagation, read-pipeline filtering for dead/unknown nodes, comparator ordering for healthy/stale/operational states, and behavior with partial EC replica sets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/ECPipelineProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/InsufficientDatanodesException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/InsufficientDatanodesException.java

## Purpose
`InsufficientDatanodesException` is an `IOException` indicating pipeline creation could not find enough datanodes.

## Important APIs, Types, And Functions
It stores `required` and `available` node counts. Constructors support remote-exception unwrapping by message only, explicit required/available/message, and default message formatting. Getters expose both counts.

## Control Flow
Placement or provider code can throw this exception when selected node count is below replication requirements. The message-only constructor sets counts to zero because remote unwrapping only supplies a message.

## State And Persistence Behavior
The exception carries transient required/available values and has no persistence.

## Dependencies And Integration Points
It extends `IOException` and is suitable for RPC propagation through Hadoop `RemoteException` unwrapping.

## Risks And Edge Cases
When reconstructed from a remote message, required and available are zero, so callers should not rely on counts unless they know the local constructor was used. Some placement code uses `SCMException` instead, so this exception is not the only insufficient-node signal.

## Test Signals
Tests should check message formatting, count getters, and remote-unwrapped constructor behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/InsufficientDatanodesException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineActionHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineActionHandler.java

## Purpose
`PipelineActionHandler` handles datanode-sent pipeline actions, currently closing pipelines when datanodes request a close.

## Important APIs, Types, And Functions
It implements `EventHandler<PipelineActionsFromDatanode>`. `onMessage` iterates pipeline actions and delegates to `processPipelineAction`. That method extracts action, pipeline ID, and detailed reason; verifies current SCM leadership; calls `pipelineManager.closePipeline` for `CLOSE`; and handles unknown pipelines with `closeUnknownPipeline`, which sends `ClosePipelineCommand` back to the reporting datanode.

## Control Flow
Non-leader SCMs log and ignore actions. Leaders process only `PipelineAction.Action.CLOSE`; unknown action types are logged as errors. If the pipeline is not found, SCM assumes the datanode has stale state and sends a close command with the current leader term through the event bus. `SCM_NOT_LEADER` errors are treated as leadership races and logged less severely.

## State And Persistence Behavior
The handler owns no state. Persistent pipeline transitions are delegated to `PipelineManager.closePipeline`; command queue persistence/delivery is delegated through `SCMEvents.DATANODE_COMMAND`.

## Dependencies And Integration Points
It depends on datanode heartbeat-dispatched `PipelineActionsFromDatanode`, protobuf `PipelineAction`, `PipelineManager`, `SCMContext`, SCM event bus, and Ozone close-pipeline commands.

## Risks And Edge Cases
Leadership can change between `isLeader` and `getTermOfLeader`, so `NotLeaderException` is handled. Unknown pipeline close commands prevent datanodes from keeping orphan pipelines, but failures to send due to leadership race leave cleanup to future reports. Only CLOSE is supported; adding new actions requires explicit handling.

## Test Signals
Tests should cover leader vs follower behavior, close action success, unknown action logging, missing-pipeline close-command emission with term, and `SCM_NOT_LEADER` handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineActionHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineFactory.java

## Purpose
`PipelineFactory` selects the appropriate `PipelineProvider` for a replication type and validates newly created pipelines.

## Important APIs, Types, And Functions
The main constructor installs providers for `STAND_ALONE`, `RATIS`, and `EC`. EC placement policy is obtained from `ContainerPlacementPolicyFactory.getECPolicy`. `create(replicationConfig, excludedNodes, favoredNodes)` delegates to the provider and validates non-null pipeline and required node count. `create(replicationConfig, nodes)` creates provider-specific pipelines from explicit nodes. `createForRead` delegates read-pipeline construction. `close` routes close behavior to the provider. Testing hooks expose and replace providers.

## Control Flow
Provider selection is a map lookup by `replicationConfig.getReplicationType()`. New write pipeline creation performs post-provider validation. Failures are surfaced as `SCMException` with internal-error or failed-to-find-healthy-nodes result codes. Provider construction fails fast with `RuntimeException` if EC placement policy cannot be created.

## State And Persistence Behavior
The factory holds an in-memory provider map. It does not persist pipelines; it returns objects to `PipelineManagerImpl`, which adds them to state and persistence.

## Dependencies And Integration Points
It depends on `NodeManager`, `PipelineStateManager`, configuration, SCM event publishing, SCM context, container placement metrics, and provider implementations. It is owned by `PipelineManagerImpl`.

## Risks And Edge Cases
A missing provider for a replication type causes null dereference rather than a clean unsupported-type exception. The node-count validation applies only to placement-aware create, not explicit-node create or read-pipeline create. Provider replacement in tests can bypass production invariants.

## Test Signals
Tests should validate provider registration, EC placement policy failure behavior, null pipeline detection, node-count mismatch detection, close delegation, and unsupported replication-type handling if new types are introduced.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManager.java

## Purpose
`PipelineManager` is the public SCM interface for pipeline lifecycle, lookup, container membership, background creation control, space-reservation checks, and pipeline metrics.

## Important APIs, Types, And Functions
Creation APIs include `createPipeline`, `buildECPipeline`, `addEcPipeline`, explicit-node creation, and `createPipelineForRead`. Lifecycle APIs include `openPipeline`, `closePipeline`, `deletePipeline`, `activatePipeline`, `deactivatePipeline`, `closeStalePipelines`, and `scrubPipelines`. Query APIs include `getPipeline`, `containsPipeline`, `getPipelines`, `getPipelineCount`, container membership getters, and `getSafeModeStatus`. Operational APIs include creator start/trigger, freeze/resume, HA reinitialization, read/write lock exposure, pending allocation check, open-container limit, and metrics retrieval.

## Control Flow
This is an interface, but it defines expected lifecycle sequencing: pipelines are created/added, opened after reports, closed before deletion, scrubbed when stale in allocated/closed states, and reinitialized from the pipeline store during SCM reload. Default `waitPipelineReady` and `waitOnePipelineReady` are no-ops/null unless implementations override them.

## State And Persistence Behavior
The interface does not own state. Implementations are expected to coordinate in-memory pipeline maps, node reverse indexes, and durable pipeline stores. `reinitialize` explicitly reloads from `Table<PipelineID, Pipeline>`.

## Dependencies And Integration Points
It extends `Closeable` and `PipelineManagerMXBean`. It integrates with SCM container manager through container membership methods, node manager through placement and allocation checks, HA DB table reload, and metrics through `SCMPipelineMetrics`.

## Risks And Edge Cases
Default wait methods can hide missing implementation if a caller uses an implementation that does not override them. Exposing locks in the interface can couple callers to implementation locking and risks deadlocks if misused. Some methods throw checked exceptions while others silently return booleans or nulls in implementations, so callers must follow concrete semantics.

## Test Signals
Contract tests should cover lifecycle ordering, persistence after reinitialize, lock behavior where exposed, allocation rollback, freeze/resume behavior, and wait method behavior for the concrete implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManagerImpl.java

## Purpose
`PipelineManagerImpl` is the HA-aware implementation of `PipelineManager`. It coordinates pipeline creation, state transitions, DB-backed state manager operations, background creation/scrubbing services, container close events, node reverse indexes, pending allocation checks, JMX, and metrics.

## Important APIs, Types, And Functions
`newPipelineManager` constructs `PipelineStateManagerImpl`, `PipelineFactory`, `BackgroundPipelineCreator`, and a periodic scrubber service, then freezes or resumes pipeline creation based on finalization checkpoint. Creation flows include `buildECPipeline`, `addEcPipeline`, `createPipeline`, `addPipelineToManager`, and explicit-node/read creation. Lifecycle flows include `openPipeline`, `closePipeline`, `deletePipeline`, `removePipeline`, `activatePipeline`, `deactivatePipeline`, `waitPipelineReady`, `waitOnePipelineReady`, and `scrubPipelines`.

Container membership and allocation APIs delegate to state manager and node manager: `addContainerToPipeline`, `removeContainerFromPipeline`, `getContainersInPipeline`, `checkSpaceAndRecordAllocation`, and `openContainerLimit`. Administrative APIs include `closeStalePipelines`, `getStalePipelines`, `sameIdDifferentHostOrAddress`, `freezePipelineCreation`, `resumePipelineCreation`, `isPipelineCreationAllowed`, `reinitialize`, and `close`.

## Control Flow
Pipeline creation first checks whether SCM is leader and safemode prechecks are complete, unless the replication factor is one, and then checks the freeze flag. It creates via `PipelineFactory`, adds through `PipelineStateManager`, and records metrics. Opening an allocated pipeline updates state to OPEN, measures latency, increments created metrics, and creates per-pipeline metrics. Closing first finalizes/open-closes all open containers in the pipeline and fires `CLOSE_CONTAINER` events, then updates pipeline state to CLOSED and removes per-pipeline metrics. Deletion removes pipeline state, updates node reverse indexes, delegates provider close behavior, and updates destroy metrics.

Scrubbing scans all pipelines. ALLOCATED pipelines older than configured timeout are closed and deleted. CLOSED pipelines older than destroy timeout are deleted. OPEN pipelines with unregistered nodes are closed, especially important for EC pipelines after SCM restart. Stale address handling finds pipelines containing the same datanode ID with a different host/IP, closes them, then deletes them.

`waitOnePipelineReady` polls candidate IDs until any pipeline is OPEN or timeout elapses, throwing if none are found or if no candidate opens in time. Pending allocation checks fetch all datanode infos for a pipeline, call node manager reservation per datanode, and rollback successful reservations if any later datanode fails.

## State And Persistence Behavior
The manager owns a `ReentrantReadWriteLock`, provider/state manager references, background service references, metrics source, MBean registration, freeze flag, SCM context, and clock. Durable pipeline state is delegated to `PipelineStateManager`, which replicates and buffers DB changes. Container close events and provider close commands are side effects outside the manager's own state. Creation freeze is in memory and reset by service initialization/finalization logic.

## Dependencies And Integration Points
It depends on SCM HA manager, DB tables, event publisher, SCM service manager, `NodeManager`, `ContainerManager`, `FinalizationManager`, `SCMContext`, `PipelineFactory`, `PipelineStateManager`, `BackgroundSCMService`, `SCMPipelineMetrics`, and Ratis utilities. It registers as `SCMPipelineManagerInfo` MBean and exposes pipeline state counts through `PipelineManagerMXBean`.

## Risks And Edge Cases
Creation checks are split between `isPipelineCreationAllowed`, factor-one bypass, and freeze state; changes to safemode/finalization behavior can accidentally permit or block pipelines. `closePipeline` closes containers before checking if the pipeline is already closed, so repeated calls can still touch containers/events. Scrubber log duration uses `Duration.between(currentTime, creationTimestamp)`, which produces negative durations when creation is before current time. Polling waits use sleep and ignore interruption except setting the interrupt flag, then continue timeout logic.

The state manager can swallow missing-pipeline removals as warnings, so callers may believe deletion succeeded. `checkSpaceAndRecordAllocation` must rollback exactly the successful prefix to avoid pending allocation leaks. Background services must be stopped before unregistering metrics/state manager close to avoid operations against closed stores.

## Test Signals
Tests should cover creation allowed/blocked in leader, follower, safemode, precheck, factor-one, and frozen states; EC build/add validation; metrics increments on allocate/open/destroy/failures; container finalization and close events on pipeline close; scrubber handling for old allocated/closed/open-with-unregistered-node pipelines; stale IP/hostname detection; wait timeout and found/not-found behavior; pending allocation rollback; reinitialize from store; MBean/metrics cleanup on close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManagerMXBean.java

## Purpose
`PipelineManagerMXBean` is the JMX management interface for pipeline manager state counts.

## Important APIs, Types, And Functions
It declares `getPipelineInfo`, returning a map from pipeline state name to count and allowing `NotLeaderException`.

## Control Flow
There is no implementation control flow. `PipelineManagerImpl.getPipelineInfo` supplies counts by iterating current pipelines.

## State And Persistence Behavior
The interface owns no state.

## Dependencies And Integration Points
It depends on Hadoop interface-audience annotations and Ratis `NotLeaderException`. Pipeline manager implementations expose it via MBeans.

## Risks And Edge Cases
The JMX contract exposes a leadership exception even though reads may be possible on followers depending on implementation. Consumers should handle missing/unavailable data.

## Test Signals
Implementation tests should verify all pipeline states are represented, zero counts are included, and leadership-related exceptions are handled by JMX callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineManagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelinePlacementPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelinePlacementPolicy.java

## Purpose
`PipelinePlacementPolicy` chooses datanodes for Ratis pipeline creation using health, space, pipeline-load limits, and rack/topology awareness.

## Important APIs, Types, And Functions
It extends `SCMCommonPlacementPolicy`. `currentRatisThreePipelineCount` counts non-closed Ratis factor-three pipelines on a datanode. `filterPipelineLimit` sorts viable datanodes by current pipeline count and filters by `nodeManager.pipelineLimit`. `filterViableNodes` applies healthy-state, space, excluded/used-node, load-limit, and multi-rack checks. `chooseDatanodesInternal` chooses randomly when topology is absent/single-rack or calls `getResultSetWithTopology`. Topology helpers include `getAnchorAndNextNode`, `chooseNode`, `chooseFirstNode`, `chooseNodeBasedOnRackAwareness`, `chooseNodeBasedOnSameRack`, and `fallBackPickNodes`.

## Control Flow
Selection starts from `NodeStatus.inServiceHealthy()` nodes. It filters nodes with enough metadata/data space, removes excluded and already-used nodes, and checks count sufficiency. It then filters by pipeline limit and detects the case where a multi-rack cluster has only one rack remaining after load filtering, failing with a specific message.

For topology-aware factor-three placement, it chooses an anchor node, tries to choose a second node on a different rack, then chooses remaining nodes preferably on the anchor rack. If same-rack topology choice fails, it falls back to random available nodes. Used-node handling supports zero, one, or two preselected nodes and rejects larger used-node sets. Required rack count is fixed at two, while max replicas per rack allows all replicas on one rack only when there is only one rack.

## State And Persistence Behavior
The policy is stateless aside from collaborator references and configured datanode pipeline limit. It reads live node and pipeline state but does not persist anything. It mutates local candidate lists during selection.

## Dependencies And Integration Points
It depends on `NodeManager`, `PipelineStateManager`, `NetworkTopology`, `RatisReplicationConfig`, `SortedList`, `SCMCommonPlacementPolicy`, and SCM config keys. It is created by `PipelinePlacementPolicyFactory` and used by `RatisPipelineProvider`.

## Risks And Edge Cases
Placement depends on current node-to-pipeline reverse indexes; stale indexes can over- or under-count pipeline load. The `checkAllNodesAreEqual` helper treats `topology.getNumOfNodes(maxLevel - 1) == 1` as all nodes equal, so topology assumptions must match `NetworkTopology` semantics. `removePeers(nextNode, healthyNodes)` is called even when `nextNode` may be null in one branch; this relies on superclass behavior tolerating null or branch conditions avoiding harm. Load failure messages use configured `datanodePipelineLimit`, but effective limits may come from `nodeManager.pipelineLimit`.

## Test Signals
Tests should cover healthy/space filtering, excluded and used nodes, pipeline-limit sorting, multi-rack failure after filtering, factor-three rack distribution, fallback selection, used-node sizes zero/one/two/too-many, single-rack behavior, current pipeline count ignoring closed/non-Ratis/non-factor-three pipelines, and interaction with dynamic per-node pipeline limits.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelinePlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelinePlacementPolicyFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelinePlacementPolicyFactory.java

## Purpose
`PipelinePlacementPolicyFactory` instantiates the configured pipeline placement policy implementation.

## Important APIs, Types, And Functions
`getPolicy` reads `OZONE_SCM_PIPELINE_PLACEMENT_IMPL_KEY` from configuration, defaulting to `PipelinePlacementPolicy`, and reflectively invokes a constructor accepting `NodeManager`, `PipelineStateManager`, and `ConfigurationSource`.

## Control Flow
The factory resolves the class, attempts constructor lookup and instantiation, and wraps any exception in a `RuntimeException` identifying the failed class.

## State And Persistence Behavior
It is a stateless utility class with a private constructor.

## Dependencies And Integration Points
It depends on `PlacementPolicy`, SCM config keys, `NodeManager`, `PipelineStateManager`, and `ConfigurationSource`. Pipeline providers use it to decouple placement algorithm selection from construction.

## Risks And Edge Cases
Custom placement policies must provide the exact constructor signature or SCM startup fails at runtime. Exceptions are unchecked, so configuration mistakes surface as service initialization failures.

## Test Signals
Tests should verify default policy construction, custom policy construction, wrong-class/wrong-constructor failure, and propagation of constructor exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelinePlacementPolicyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineProvider.java

## Purpose
`PipelineProvider` is the abstract base for replication-type-specific pipeline creation and close logic.

## Important APIs, Types, And Functions
Subclasses implement placement-aware `create`, explicit-node `create`, read `createForRead`, and `close`. The base stores `NodeManager` and `PipelineStateManager`. Helper methods `pickNodesNotUsed` and `pickAllNodesNotUsed` select in-service healthy nodes not already used by open, dormant, or allocated pipelines with the same replication config, optionally enforcing metadata/data space requirements.

## Control Flow
`pickAllNodesNotUsed` collects all datanodes used by active pipelines for the requested replication config, then filters healthy nodes to those not in that set. It throws `SCMException` if fewer candidates exist than required. `pickNodesNotUsed` limits to required count; the size-aware variant additionally filters with `SCMCommonPlacementPolicy.hasEnoughSpace` before limiting and throws a space-specific `SCMException` if insufficient.

## State And Persistence Behavior
The provider base is stateless aside from manager references. It reads pipeline state and node state but does not mutate or persist them.

## Dependencies And Integration Points
It depends on `ReplicationConfig`, `PipelineStateManager`, `NodeManager`, `NodeStatus`, `ContainerReplica`, `SCMCommonPlacementPolicy`, and `SCMException`. `SimplePipelineProvider`, `RatisPipelineProvider`, and `ECPipelineProvider` extend it.

## Risks And Edge Cases
The no-arg constructor sets managers to null for tests/subclasses; helper methods will fail if used on such instances. Parallel stream filtering depends on correct `DatanodeDetails.equals`. Selection order is not strongly defined after parallel collection, which can affect deterministic tests. Active-state filtering excludes only OPEN, DORMANT, and ALLOCATED pipelines.

## Test Signals
Tests should cover node exclusion by active pipelines, closed pipelines not excluding nodes, insufficient healthy nodes, insufficient space, required-node limiting, and behavior of subclasses using explicit vs helper-based placement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineReportHandler.java

## Purpose
`PipelineReportHandler` processes pipeline reports sent by datanodes during heartbeats. It records reported datanodes and leaders, opens healthy allocated pipelines, notifies safemode rules, and commands datanodes to close unknown pipelines.

## Important APIs, Types, And Functions
It implements `EventHandler<PipelineReportFromDatanode>`. `onMessage` validates the report wrapper and iterates each protobuf `PipelineReport`. `processPipelineReport` resolves the pipeline, calls `setReportedDatanode`, calls `setPipelineLeaderId`, opens allocated healthy pipelines, and fires `OPEN_PIPELINE` while SCM is in safemode. `handlePipelineNotFoundException` sends `ClosePipelineCommand` to the reporting datanode if SCM is leader. `isNotLeaderException` suppresses noisy follower errors.

## Control Flow
For each reported pipeline, missing pipeline IDs are handled separately from other IO/timeouts. Existing pipelines mark the reporting datanode through `pipeline.reportDatanode`. If the report says the datanode is leader, or the pipeline is Ratis factor one where no leader flag exists, the pipeline leader ID is set to that datanode. Allocated pipelines transition to open only after `pipeline.isHealthy()` becomes true, meaning enough expected reports have arrived. Healthy reports in safemode fire an event for safemode exit rules.

## State And Persistence Behavior
The handler mutates `Pipeline` objects in memory by recording reported nodes and leader ID. Opening a pipeline delegates to `PipelineManager.openPipeline`, which persists state through the state manager. Unknown-pipeline close commands are queued through the event bus.

## Dependencies And Integration Points
It depends on datanode heartbeat dispatcher wrappers, `SafeModeManager`, `PipelineManager`, `SCMContext`, SCM events, protobuf reports, Ratis replication config helpers, and close-pipeline commands.

## Risks And Edge Cases
Follower SCMs may attempt operations that throw `SCM_NOT_LEADER`; the handler suppresses those only for `SCMException`. Unknown pipelines are only commanded closed by leaders. Pipeline object mutation through `reportDatanode` and `setLeaderId` must be thread-safe with concurrent reads. Factor-one leader assignment assumes the reporter is the only/valid leader.

## Test Signals
Tests should cover allocated pipeline opening only after all required reports, leader ID assignment for factor one and leader-flag reports, safemode `OPEN_PIPELINE` event emission, unknown-pipeline close command emission, follower/no-leader behavior, and exception handling for IO/timeouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateManager.java

## Purpose
`PipelineStateManager` defines the replicated state-management contract for SCM pipelines and their container memberships.

## Important APIs, Types, And Functions
Replicated methods marked with `@Replicate` include `addPipeline`, `removePipeline`, and `updatePipelineState`, each using protobuf IDs/states suitable for SCM Ratis. Non-replicated methods manage container membership, lookup pipelines by ID/config/state, count pipelines, close, and reinitialize from a DB table. The default `getType` returns SCM Ratis request type `PIPELINE`.

## Control Flow
Implementations are expected to replicate pipeline add/remove/state-update operations through SCM HA before applying them. Container membership changes are local state operations around the pipeline state map and are not annotated in this interface.

## State And Persistence Behavior
The interface does not own state but explicitly models a persistent `Table<PipelineID, Pipeline>` reload path. Implementations must keep in-memory state and durable state consistent.

## Dependencies And Integration Points
It extends `SCMHandler`, uses SCM Ratis protocol request types, DB table abstractions, `ReplicationConfig`, `Pipeline`, `PipelineID`, `ContainerID`, and SCM metadata replication annotations. `PipelineManagerImpl` is the primary caller.

## Risks And Edge Cases
Clear separation between replicated and non-replicated methods is critical. If callers bypass replicated paths for add/remove/state transitions, HA followers can diverge. Reinitialize must also rebuild node reverse indexes, not just pipeline maps.

## Test Signals
Tests should validate replication annotations/proxy behavior, DB reload, pipeline lookup filters, container membership rules, and consistency between pipeline store and node manager after add/remove/reinitialize.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateManagerImpl.java

## Purpose
`PipelineStateManagerImpl` is the concrete in-memory and DB-buffered implementation of `PipelineStateManager`, wrapped by an SCM Ratis proxy for replicated pipeline mutations.

## Important APIs, Types, And Functions
The builder accepts a pipeline DB table, node manager, SCM Ratis server, and DB transaction buffer, initializes the state map from the table, and returns a proxy handler. `initialize` loads persisted pipelines and repopulates node-to-pipeline membership. `addPipeline`, `removePipeline`, and `updatePipelineState` update `PipelineStateMap`, update `NodeManager` reverse indexes where needed, and buffer DB writes/removes. Read APIs delegate to `PipelineStateMap` under a read lock. Container membership methods add, force-add, remove, and list containers. `close` nulls the store, and `reinitialize` rebuilds state from a new table.

## Control Flow
`addPipeline` converts the protobuf pipeline to a `Pipeline`, then under write lock adds it to the state map, records node memberships, and adds it to the transaction buffer. `removePipeline` removes from the state map, removes node memberships, and buffers DB deletion; missing pipelines are logged as warnings because duplicate close/delete paths can occur. `updatePipelineState` converts protobuf state, updates the state map, then buffers the updated pipeline object. `removeContainerFromPipeline` deliberately swallows missing-pipeline exceptions because close-container and pipeline-close events can race through Ratis replay.

## State And Persistence Behavior
The class owns `PipelineStateMap`, `NodeManager`, a nullable `Table<PipelineID, Pipeline>`, `DBTransactionBuffer`, and a read/write lock. Persistence is transactional-buffer based rather than immediate direct table writes. When `pipelineStore` is null after close, mutations are skipped to avoid writes against a closed store. Reinitialize replaces both map and store and reloads from DB.

## Dependencies And Integration Points
It depends on `PipelineStateMap`, `NodeManager`, SCM HA Ratis proxy/invoker, DB table/iterator abstractions, transaction buffer, and pipeline/container types. It is constructed by `PipelineManagerImpl.newPipelineManager`.

## Risks And Edge Cases
Initialization must rebuild node reverse indexes exactly once; duplicate initialization without clearing node manager could over-retain memberships. Null `pipelineStore` silently prevents mutations after close, which protects shutdown but can hide late event activity. Missing-pipeline warnings are tolerated for idempotence, but excessive swallowing could mask real consistency bugs. `updatePipelineState` calls `getPipeline` while holding the write lock; this relies on the same `ReentrantReadWriteLock` allowing a writer thread to acquire the read lock.

## Test Signals
Tests should cover load from non-empty store, add/remove/update DB buffer operations, node manager add/remove pipeline calls, missing-pipeline idempotence, container membership add/remove/force rules, close behavior with null store, reinitialize replacing state, and Ratis proxy wrapping through the builder.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateManagerImpl.java -->

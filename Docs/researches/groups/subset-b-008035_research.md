# subset-b-008035 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/package-info.java

Purpose: This package descriptor declares `org.apache.hadoop.hdds.scm.metadata` as the Storage Container Manager metadata layer. It is documentation-only code, but it anchors the package that contains SCM DB definitions, metadata-store implementation, and codecs used by server-side SCM persistence.

Important APIs and types: The file exports no classes or functions. Its only API-level effect is the package declaration and package Javadoc.

Control flow: There is no runtime control flow. Java tooling associates the package comment with the generated package documentation for metadata-layer classes.

State and persistence behavior: This file does not store state. Its package is associated with persistent SCM metadata components elsewhere, so the main integration signal is naming and package ownership rather than behavior.

Dependencies and integration points: It integrates only with Java package documentation generation and the compiler. Downstream classes in the same package provide RocksDB/table definitions and certificate/key codecs.

Risks: The main risk is documentation drift if the package grows beyond metadata-store concerns. Because it has no executable code, behavioral regressions come only from package relocation or deletion affecting source organization and generated docs.

Test signals: No direct tests are expected. Build compilation and Javadoc/package checks are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/CommandQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/CommandQueue.java

Purpose: `CommandQueue` is the SCM-side per-datanode queue of `SCMCommand<?>` objects to be delivered on subsequent datanode heartbeats. It is explicitly not thread-safe, so callers such as `SCMNodeManager` must protect access with their own lock.

Important APIs and types: The public surface includes `addCommand(DatanodeID, SCMCommand<?>)`, `getCommandsInQueue()`, `getDatanodeCommandCount(DatanodeID, Type)`, `getDatanodeCommandSummary(DatanodeID)`, and test-only `clear()`. Package-private `getCommand(DatanodeID)` drains all commands for a datanode. The private `Commands` holder tracks command order plus a `Map<SCMCommandProto.Type, Integer>` summary.

Control flow: Adding a command creates or finds the datanode's `Commands`, appends the command, updates the type summary only when `SCMCommand.contributesToQueueSize()` is true, and increments the global `commandsInQueue`. Draining removes the datanode entry from `commandMap`, returns the previous ordered list, clears per-node summaries, and subtracts the returned list size from the global counter.

State and persistence behavior: All state is in-memory: `commandMap`, per-node command lists, summaries, and the global count. Commands are not persisted in this class, so an SCM restart loses queued commands unless higher layers regenerate them.

Dependencies and integration points: It depends on `DatanodeID`, datanode protocol command types, and Ozone `SCMCommand`. `DeadNodeHandler` clears a dead node's queue through `NodeManager.getCommandQueue`, and heartbeat handling uses queue summaries to merge SCM-side pending commands with datanode-reported queued counts.

Risks: The class relies on external synchronization; unsynchronized callers can corrupt counts or lose commands. `commandsInQueue` counts all drained commands, while summaries omit commands that do not contribute to queue size, so global count and summary totals intentionally differ. Draining subtracts the entire returned list size, so any future non-queued or synthetic command semantics need review.

Test signals: Useful tests should cover FIFO drain order, empty-list behavior, global count reset after drain and clear, type summary copies being caller-safe, non-contributing commands excluded from summaries, and external lock discipline in callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/CommandQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitor.java

Purpose: `DatanodeAdminMonitor` defines the monitor contract for decommission, recommission, and maintenance workflows. It is a `Runnable` so `NodeDecommissionManager` can schedule periodic workflow ticks.

Important APIs and types: The interface exposes `startMonitoring`, `stopMonitoring`, `getTrackedNodes`, `setMetrics`, and `getContainersPendingReplication`. Its current tracked-node type is the implementation class `DatanodeAdminMonitorImpl.TrackedNode`, and pending-container output is keyed by strings such as `UnderReplicated` and `UnClosed`.

Control flow: Implementations accept nodes into a monitored workflow, queue cancellation/recommission requests, update metrics, and answer progress queries. The actual periodic behavior is implemented by `DatanodeAdminMonitorImpl.run`.

State and persistence behavior: The interface defines no state, but implementers maintain in-memory workflow queues and snapshots. Workflow progress is reflected through node operational state in `NodeManager`; durable recovery relies on datanodes re-registering their persisted operational state and the decommission manager resuming monitoring.

Dependencies and integration points: It couples node administration to `DatanodeDetails`, `ContainerID`, `NodeDecommissionMetrics`, and `NodeNotFoundException`. It is owned by `NodeDecommissionManager` and observed by CLI/JMX-style progress calls.

Risks: Exposing `DatanodeAdminMonitorImpl.TrackedNode` in the interface leaks the implementation. The `Map<String, List<ContainerID>>` return shape is stringly typed, so callers must know exact category names.

Test signals: Contract tests should verify that starting, stopping, tracking, metrics assignment, and pending-replication queries behave consistently through the interface, not only the concrete monitor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitorImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitorImpl.java

Purpose: `DatanodeAdminMonitorImpl` is the periodic workflow engine for decommissioning, maintenance, and recommissioning datanodes. It closes pipelines, waits for containers to become safely replicated or closed, changes node operational states, and emits progress metrics.

Important APIs and types: Key public methods are `startMonitoring`, `stopMonitoring`, `run`, `getTrackedNodes`, `setMetrics`, and `getContainersPendingReplication`. `TrackedNode` stores the datanode, workflow start time, and last observed under-replicated/unclosed container IDs. Important collaborators are `NodeManager`, `ReplicationManager`, `EventPublisher`, `NodeDecommissionMetrics`, `ContainerReplicaCount`, `ReplicationManagerReport`, `SCMEvents.START_ADMIN_ON_NODE`, and `PipelineID`.

Control flow: `run()` clears per-host state, synchronizes to process cancelled nodes first, moves pending nodes into `trackedNodes`, then scans tracked nodes. Each tracked node must still be in a decommission or maintenance operational state and must not be dead unless already `IN_MAINTENANCE`. For decommissioning or entering-maintenance nodes, it waits until pipelines are closed, confirms the datanode has persisted the target op state, checks every hosted container for closure and replication health, then completes decommission or moves the node into maintenance. Maintenance nodes are returned to service automatically when their expiry has passed.

State and persistence behavior: The monitor's own queues and metrics counters are in-memory. Persistent workflow state is represented indirectly by `NodeManager.setNodeOperationalState`, and the code requires `status.getOperationalState() == dn.getPersistedOpState()` before finalizing decommission or maintenance entry. `TrackedNode.containersReplicatedOnNode` stores the last pending-replication categories for progress reporting.

Dependencies and integration points: It integrates with pipeline close events, container health evaluation, replication-manager scheduling, SCM events, and metrics. `NodeDecommissionManager` schedules it and calls its start/stop methods. The replication check ignores DELETED and DELETING containers and uses `ReplicationManager.checkContainerStatus` to determine if under-replication remains.

Risks: The monitor catches all exceptions to keep the scheduled thread alive, which prevents crash loops but can hide repeated failures behind logs. `trackedNodes` is concurrent but iteration/removal plus synchronized queue processing must be kept consistent. Metrics synchronization assumes `metrics` is set before `run`; a null metrics object would fail. Pending container categories use literal string keys. Workflow can stall if pipelines never close, if a datanode never persists its op state, or if containers stay unclosed/under-replicated.

Test signals: Strong tests should cover pending-to-tracked transition, cancellation/recommission, pipeline waiting metrics, container replication categorization, DELETED/DELETING container skips, dead-node abort behavior, persisted-op-state gating, maintenance expiry, per-host metrics snapshots, and `getContainersPendingReplication` contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitorImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeInfo.java

Purpose: `DatanodeInfo` extends `DatanodeDetails` with SCM runtime metadata: last heartbeat, storage reports, metadata-volume reports, node status, command counts, layout versions, failed-volume counts, and pending container allocation tracking.

Important APIs and types: Important methods include `updateLastHeartbeatTime`, `updateLastKnownLayoutVersion`, `updateStorageReports`, `updateMetaDataStorageReports`, `getNodeStatus`, `setNodeStatus`, `setCommandCounts`, `getCommandCount`, and `getPendingContainerAllocations`. It uses `ReadWriteLock`, `LayoutVersionProto`, `StorageReportProto`, `MetadataStorageReportProto`, `CommandQueueReportProto`, and `PendingContainerTracker.TwoWindowBucket`.

Control flow: Construction copies base datanode details, initializes heartbeat time, normalizes layout versions, creates empty reports and command maps, and creates a per-node pending-container bucket. Report update methods compute derived counters and replace snapshots under the write lock. `setCommandCounts` clears the previous heartbeat command counts, reads each command/count pair from the datanode report, normalizes negative values to zero, adds any SCM-side commands that will be sent in the current heartbeat, and preserves entries not reported by the datanode.

State and persistence behavior: This is volatile SCM memory. The only persistent input is the datanode's own details and persisted operational state copied into `NodeStatus` elsewhere. Storage and command snapshots are replaced on heartbeat reports; pending allocations age through a two-window bucket.

Dependencies and integration points: `NodeStateManager` creates and updates `DatanodeInfo`; `SCMNodeManager` uses it for heartbeat processing, storage accounting, command queue visibility, placement decisions, and MXBean reporting. Upgrade logic uses the last known layout version to move nodes between `HEALTHY` and `HEALTHY_READONLY`.

Risks: The class warns that lost updates are possible if callers read, mutate, and write `NodeStatus` without higher-level coordination. Report lists are stored by reference, so callers should avoid mutating lists after update. `lastStatsUpdatedTime` is not read under lock. Unknown command types are skipped, which can mask version skew while keeping SCM running.

Test signals: Tests should cover lock-safe heartbeat updates, storage failed-volume counts, metadata volume counts, layout version update ignoring nulls, command count replacement/merge semantics, unknown and negative command report handling, pending bucket rolling, and equality inherited from `DatanodeDetails`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeUsageInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeUsageInfo.java

Purpose: `DatanodeUsageInfo` bundles `DatanodeDetails` with capacity, usage, container count, pipeline count, reserved bytes, and optional filesystem-level usage for client/admin views and sorting.

Important APIs and types: Important methods are `calculateUtilization`, `getMostUtilized`, getters/setters for datanode/stat/count fields, `setFilesystemUsage`, `equals`, `hashCode`, and `toProto(int clientVersion)`. It wraps `SCMNodeStat` and emits `HddsProtos.DatanodeUsageInfoProto`.

Control flow: Utilization is calculated as `(capacity - remaining + plusSize) / capacity`, returning zero for zero capacity and intentionally not using SCM-used bytes. The comparator delegates to utilization and treats equal datanode identity as equal. `toProtoBuilder` conditionally writes datanode details and SCM stats, then always writes counts/reserved and optional filesystem usage.

State and persistence behavior: The object is an in-memory DTO. Defaults for container and pipeline counts are `-1`, indicating unknown. Filesystem usage is present only after `setFilesystemUsage`.

Dependencies and integration points: `NodeManager.getMostOrLeastUsedDatanodes` and usage APIs expose instances of this class to admin/client callers. It depends on `SCMNodeStat` counters and datanode protobuf conversion.

Risks: Equality is based only on datanode details, not current usage, so collections can treat two different usage snapshots for the same datanode as duplicates. The utilization comparator can produce equal order for distinct nodes with the same utilization. Proto output uses SCM-used for the `used` field even though utilization uses capacity-minus-remaining, so callers must understand the distinction.

Test signals: Tests should cover zero-capacity utilization, plus-size utilization, comparator ordering, proto field population with and without optional filesystem usage, unknown count defaults, and equality/hash behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeUsageInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DeadNodeHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DeadNodeHandler.java

Purpose: `DeadNodeHandler` handles `SCMEvents.DEAD_NODE` by cleaning up SCM state associated with a datanode that is currently dead. It closes open containers, destroys pipelines, removes replicas when appropriate, notifies replication manager, clears command queues, updates deleted-block tracking, and removes the node from network topology if it is still dead.

Important APIs and types: It implements `EventHandler<DatanodeDetails>`. Collaborators include `NodeManager`, `PipelineManager`, `ContainerManager`, optional `DeletedBlockLog`, `NetworkTopology`, `ContainerInfo`, `ContainerReplica`, and event types `CLOSE_CONTAINER` and `REPLICATION_MANAGER_NOTIFY`.

Control flow: `onMessage` first re-reads the current `NodeStatus` and ignores stale events if the node is no longer `DEAD`. It closes any OPEN containers by firing `CLOSE_CONTAINER`, closes and deletes pipelines on the node, skips replica and deleted-block cleanup for nodes in maintenance, notifies replication manager for non-maintenance dead nodes, drains the node command queue, and finally rechecks health before removing the node from topology.

State and persistence behavior: The handler mutates in-memory SCM maps, pipeline manager state, container replica membership, command queue state, topology membership, and deleted-block log state. Pipeline/container manager changes may touch their backing metadata stores depending on the implementation. It does not remove `NodeStateManager` entries.

Dependencies and integration points: It depends on node state transitions emitted by `NodeStateManager`. It coordinates with replication manager through an event, with deleted-block cleanup through `DeletedBlockLog.onDatanodeDead`, and with placement policy through topology removal.

Risks: It must tolerate races where a node resurrects while the dead event is being handled; the final health recheck protects topology removal. Maintenance nodes deliberately keep replicas and delete-block commands, so incorrect maintenance state can change replication behavior. Pipeline cleanup catches IO failures and continues, leaving possible stale pipelines.

Test signals: Tests should cover stale dead-event skip, container close event emission, pipeline close/delete calls, maintenance vs non-maintenance replica handling, deleted-block callback, command queue drain, topology removal only when still dead, and `NodeNotFoundException` logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DeadNodeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/HealthyReadOnlyNodeHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/HealthyReadOnlyNodeHandler.java

Purpose: `HealthyReadOnlyNodeHandler` handles transitions into `HEALTHY_READONLY`, mainly during layout-version mismatch or upgrade finalization. It resends pipeline close commands so containers in CLOSING can reach CLOSED, and ensures the datanode is present in network topology.

Important APIs and types: It implements `EventHandler<DatanodeDetails>` and depends on `NodeManager`, `PipelineManager`, `PipelineID`, `Pipeline`, and `NetworkTopology`.

Control flow: On event, it gets all pipelines for the node, loads each pipeline, logs its state, and calls `pipelineManager.closePipeline` without force deletion. After pipeline handling, it unconditionally adds the node back to topology and verifies the `DatanodeDetails` stored by `NodeManager` has a parent.

State and persistence behavior: It mutates pipeline state by queuing close behavior in the pipeline manager and mutates in-memory topology membership. It does not directly persist node state or pipeline deletion.

Dependencies and integration points: `NodeStateManager` fires this event on layout mismatch, dead/stale restoration to readonly, or forced finalization transitions. Upgrade services rely on this handler to unblock datanode finalization by nudging closing containers.

Risks: `nodeManager.getPipelines` must not return null; the code iterates directly. IOException on one pipeline is logged and does not stop later topology add. The unconditional topology add is intentionally race-safe against dead-node removal, but the parent assertion can fail if topology/node-map integration is broken.

Test signals: Tests should verify close calls for all known pipelines, IOException tolerance, idempotent topology add for existing nodes, parent non-null after re-add, and behavior when a node has no pipelines.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/HealthyReadOnlyNodeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/InvalidHostStringException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/InvalidHostStringException.java

Purpose: `InvalidHostStringException` is a checked exception used when `NodeDecommissionManager` cannot parse or understand a user-supplied host or `host:port` string.

Important APIs and types: It extends `IOException` and provides message-only and message-plus-cause constructors.

Control flow: There is no internal control flow. `NodeDecommissionManager.HostDefinition` throws it for invalid URI parsing or missing host components, and command paths convert it into `DatanodeAdminError`.

State and persistence behavior: The exception carries no additional state beyond standard exception message and cause. It has no persistence behavior.

Dependencies and integration points: It integrates decommission/maintenance host parsing with admin error reporting and existing IOException-based signatures.

Risks: The message text is user-visible through admin errors, so changes can affect CLI tests. Extending `IOException` means it can be grouped with network/lookup failures, which is convenient but can blur parse vs IO causes.

Test signals: Tests should cover invalid host strings, malformed URI inputs, blank host components, cause preservation, and conversion to `DatanodeAdminError`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/InvalidHostStringException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/InvalidNodeStateException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/InvalidNodeStateException.java

Purpose: `InvalidNodeStateException` is a checked exception thrown when an admin operation such as decommission or maintenance is requested for a datanode in an incompatible operational state.

Important APIs and types: It extends `IOException` with message-only and message-plus-cause constructors.

Control flow: The exception is thrown by `NodeDecommissionManager.startDecommission` and `startMaintenance` when a node is not `IN_SERVICE`, already in the relevant workflow, or otherwise not eligible. Higher-level bulk methods convert it to `DatanodeAdminError`.

State and persistence behavior: The class stores only standard exception message/cause. It does not mutate state; the caller should throw it before changing node operational state.

Dependencies and integration points: It links node status validation to admin APIs and CLI-visible error paths. It is part of the decommission-manager API contract.

Risks: The class Javadoc currently says "host strings", which appears copied from `InvalidHostStringException` and can mislead maintainers. Message wording is likely asserted by admin-path tests or visible to users.

Test signals: Tests should verify that invalid state transitions throw this exception without calling `setNodeOperationalState` and that bulk admin APIs surface its message in error results.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/InvalidNodeStateException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NewNodeHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NewNodeHandler.java

Purpose: `NewNodeHandler` handles newly registered datanode events by closing stale pipelines, notifying SCM services, and resuming decommission or maintenance workflows if the datanode reports a persisted non-`IN_SERVICE` operational state.

Important APIs and types: It implements `EventHandler<DatanodeDetails>` and uses `PipelineManager.closeStalePipelines`, `NodeDecommissionManager.continueAdminForNode`, `SCMServiceManager.notifyEventTriggered`, and `SCMService.Event.NEW_NODE_HANDLER_TRIGGERED`.

Control flow: On event, it closes stale pipelines for the datanode, notifies service listeners, then checks `datanodeDetails.getPersistedOpState`. If the persisted state is not `IN_SERVICE`, it asks the decommission manager to continue the admin workflow. `NodeNotFoundException` is logged as unexpected.

State and persistence behavior: It mutates pipeline state through the pipeline manager and may re-enqueue the datanode into the in-memory admin monitor. It relies on persisted operational state reported by the datanode at registration.

Dependencies and integration points: It connects registration, pipeline recovery, HA/service readiness notifications, and admin workflow recovery after SCM restart or datanode re-registration.

Risks: Continuing admin workflow is leader-gated inside the decommission manager, so followers ignore it. If pipeline close fails through unchecked exceptions, later workflow recovery will not run. The handler assumes the node was just registered, so `NodeNotFoundException` is only logged.

Test signals: Tests should verify stale pipeline close, service event notification, conditional `continueAdminForNode`, leader/follower behavior through manager tests, and exception logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NewNodeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeAddressUpdateHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeAddressUpdateHandler.java

Purpose: `NodeAddressUpdateHandler` handles datanode IP or hostname changes. It closes stale pipelines, notifies SCM service observers, and asks the decommission manager to continue any admin workflow for the updated datanode.

Important APIs and types: It implements `EventHandler<DatanodeDetails>` and depends on `PipelineManager`, `NodeDecommissionManager`, `SCMServiceManager`, and `SCMService.Event.NODE_ADDRESS_UPDATE_HANDLER_TRIGGERED`.

Control flow: `onMessage` logs the address update context, calls `pipelineManager.closeStalePipelines`, notifies the service manager, and calls `decommissionManager.continueAdminForNode` unconditionally. `NodeNotFoundException` is logged as an error.

State and persistence behavior: It can mutate pipeline state and in-memory admin-monitor tracking. It does not persist address information itself; the updated datanode details are already in node-manager state before this handler runs.

Dependencies and integration points: It connects node registration/update handling with pipeline cleanup and decommission/maintenance workflow recovery. It is useful when the same datanode identity appears with updated network coordinates.

Risks: Unlike `NewNodeHandler`, it calls `continueAdminForNode` even if the node is currently `IN_SERVICE`; the manager checks state and only monitors admin states. Errors from stale pipeline close outside `NodeNotFoundException` would abort service notification and admin continuation.

Test signals: Tests should cover stale pipeline close calls, service notification, continuation call, and `NodeNotFoundException` logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeAddressUpdateHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeDecommissionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeDecommissionManager.java

Purpose: `NodeDecommissionManager` is the external control plane for starting, resuming, and stopping decommission and maintenance workflows. It resolves host strings to datanodes, validates capacity/redundancy preconditions, changes operational states, schedules the admin monitor, and owns decommission metrics.

Important APIs and types: Key APIs are `decommissionNodes`, `startDecommission`, `recommissionNodes`, `recommission`, `startMaintenanceNodes`, `startMaintenance`, `continueAdminForNode`, `onBecomeLeader`, `getContainersPendingReplication`, and `stop`. `HostDefinition` parses `hostname` or `hostname:port`. Dependencies include `NodeManager`, `ContainerManager`, `ReplicationManager`, `SCMContext`, `DatanodeAdminMonitor`, `NodeDecommissionMetrics`, `DatanodeAdminError`, `ContainerInfo`, and `ECReplicationConfig`.

Control flow: Construction configures hostname vs IP matching, monitor interval, maintenance redundancy knobs, creates the monitor and metrics, and schedules the monitor at a fixed rate. Bulk admin methods resolve host strings to datanodes, optionally run a fail-early redundancy check unless `force` is true, then call per-node start methods. Decommission transitions `IN_SERVICE` nodes to `DECOMMISSIONING`; maintenance transitions them to `ENTERING_MAINTENANCE` with optional expiry. Recommission queues non-`IN_SERVICE` nodes for monitor cancellation. Leader election calls `onBecomeLeader`, which re-adds any already-admin nodes to the monitor.

State and persistence behavior: The manager owns a scheduled executor and in-memory metrics/monitor. Durable workflow state is the node operational state set through `NodeManager`; datanodes persist and report that state, allowing `continueAdminForNode` to resume after restart or leadership changes. No separate decommission DB is written here.

Dependencies and integration points: It integrates CLI/admin requests, DNS resolution, node lookup by address, container placement safety checks, EC and non-EC replication constraints, HA leadership (`SCMContext.isLeader`), event-queue-driven monitor actions, and metrics registration.

Risks: Host resolution can be ambiguous when multiple datanodes share a host; the code falls back to port matching or most recent heartbeat only when all ports match. Redundancy preflight uses cluster-level in-service healthy counts rather than full per-placement topology checks. The `validDns` construction in maintenance is redundant and easy to misread. Scheduled monitor startup happens in the constructor, so tests must stop it. Force bypasses safety checks and can allow under-replication.

Test signals: Tests should cover host parsing and DNS/IP mode, multiple datanodes per host with port matching, ambiguity errors, decommission/maintenance force and non-force paths, EC maintenance minimum calculation, state transition validation, recommission cancellation, leader-only continuation, monitor scheduling, metrics unregister on stop, and pending-replication query forwarding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeDecommissionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeDecommissionMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeDecommissionMetrics.java

Purpose: `NodeDecommissionMetrics` publishes aggregate and per-host metrics for decommission and maintenance workflows. It tracks monitored nodes, recommissioning nodes, pipelines waiting to close, under-replicated containers, unclosed containers, sufficiently replicated containers, and workflow start times.

Important APIs and types: The class is a Hadoop `MetricsSource` annotated with `@Metrics`. Public methods include `create`, `getMetrics`, `unRegister`, setter/getter pairs for aggregate gauges, and `metricRecordOfContainerStateByHost`. The nested `ContainerStateInWorkflow` holds per-host counters and `MetricsInfo` descriptors.

Control flow: `create()` registers the metrics source with `DefaultMetricsSystem`. `DatanodeAdminMonitorImpl` periodically sets aggregate gauges and replaces the per-host map. `getMetrics` snapshots aggregate gauges into one record, then emits additional tagged records for each host in `metricsByHost`.

State and persistence behavior: Metrics are in-memory only and reset on SCM restart. The per-host map is copied from monitor snapshots, not incrementally accumulated. `unRegister` removes the source from the metrics system during manager shutdown.

Dependencies and integration points: It integrates monitor progress with Hadoop metrics2, Ozone metrics context, JMX/metrics sinks, and tests through visible getters.

Risks: `getMetrics` manually chains records with `endRecord`; changes must preserve metrics2 expectations. The per-host map key is host string, so duplicate hostnames or hostname changes can overwrite records. All mutating methods are synchronized, limiting races but making long metrics collection a possible contention point.

Test signals: Tests should verify registration/unregistration, aggregate gauge setters/getters, per-host metric replacement, missing-host visible getters returning null, and metrics snapshot containing both aggregate and tagged host records.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeDecommissionMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeManager.java

Purpose: `NodeManager` is the central SCM interface for datanode registration, heartbeat processing, node state queries, storage statistics, command delivery, container/pipeline membership, topology access, admin state changes, pending allocation tracking, and MXBean reporting.

Important APIs and types: It extends `StorageContainerNodeProtocol`, `EventHandler<CommandForDatanode>`, `NodeManagerMXBean`, and `Closeable`. Important methods include `register`, `getNodes`, `getNodeCount`, `getAllNodes`, `getStats`, `getNodeStats`, `getMostOrLeastUsedDatanodes`, `getUsageInfo`, `getDatanodeInfo`, `checkSpaceAndRecordAllocation`, `removePendingAllocationForDatanode`, `getNodeStatus`, `setNodeOperationalState`, pipeline/container membership methods, command queue methods, report processing methods, `getNodesByAddress`, `getLastHeartbeat`, `getClusterNetworkTopologyMap`, `removeNode`, `openContainerLimit`, and `getPendingContainerTracker`.

Control flow: As an interface, it defines expected behavior rather than implementing it. Registration can default missing layout info to the current default layout version. Heartbeat/report processing should update node status, reports, command counts, command queues, and layout versions. Admin calls change operational state, while health state transitions are usually driven by `NodeStateManager`.

State and persistence behavior: Implementations own in-memory node, command, topology, pipeline, container, and stats state. Node operational state is the important persistent contract because datanodes store and report it. The interface also exposes pending-container allocations that age in SCM memory to prevent over-allocation between reports.

Dependencies and integration points: This interface sits at the boundary between SCM, datanode RPCs, events, placement policies, pipeline manager, container manager, decommission manager, metrics/JMX, upgrade layout manager, and command send-notification hooks.

Risks: The interface is broad, so implementation changes can affect many subsystems. Some methods return nullable values or default no-ops, which can hide unsupported behavior in tests. Command counts combine datanode-reported queued commands and SCM-side queued commands; consistency depends on locking in implementations.

Test signals: Implementation tests should cover registration with and without layout info, node state/count filters, stats aggregation, usage sorting, command queue accounting, report processing, pending allocation accounting, topology membership, remove-node restrictions, operational-state event firing, and MXBean map contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeManagerMXBean.java

Purpose: `NodeManagerMXBean` defines the JMX management view for SCM node manager information.

Important APIs and types: It exposes `getNodeCount`, `getNodeInfo`, `getNodeStatusInfo`, and default `getNodeStatistics`. Return types are string-keyed maps suitable for JMX serialization.

Control flow: The interface has no executable flow beyond the default `getNodeStatistics`, which returns an empty map. Implementations are expected to build node counts by health/operational state, disk metrics, status table entries, and optional statistics.

State and persistence behavior: The MXBean reads current node-manager state and exposes snapshots. It does not persist anything.

Dependencies and integration points: `NodeManager` extends this interface, allowing its implementation to register with JMX/metrics management. It uses `InterfaceAudience.Private` to mark it internal to Ozone.

Risks: String-keyed nested maps are flexible but not type-safe; changing key names can break dashboards and tests. The default empty statistics map can mask missing implementation support.

Test signals: Tests should verify that implementation maps contain expected state buckets, disk metrics, status fields, and optional statistics keys without null structures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeManagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeReportHandler.java

Purpose: `NodeReportHandler` handles datanode node-report events and forwards storage/metadata report content to `NodeManager`.

Important APIs and types: It implements `EventHandler<SCMDatanodeHeartbeatDispatcher.NodeReportFromDatanode>`. It depends on `NodeManager.processNodeReport`, `DatanodeDetails`, and `NodeReportProto`.

Control flow: The constructor requires a non-null node manager. `onMessage` requires a non-null event object and datanode details, then calls `nodeManager.processNodeReport(dn, report)`.

State and persistence behavior: This handler has no mutable state beyond its node-manager reference. State updates occur inside the node manager, which refreshes datanode storage reports and derived stats.

Dependencies and integration points: It is part of heartbeat dispatch: datanode reports are unpacked by `SCMDatanodeHeartbeatDispatcher`, routed through the event bus, and applied to node-manager state.

Risks: Null events or missing datanode details fail fast with `NullPointerException`, which is appropriate for malformed internal events but may surface if dispatcher contracts change. It does not catch node-manager exceptions.

Test signals: Tests should verify non-null validation and exact forwarding of datanode details plus report to `processNodeReport`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeStateManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeStateManager.java

Purpose: `NodeStateManager` is the in-memory source of truth for SCM datanode health state, operational state, container membership, pipeline membership, heartbeat timestamps, and layout-version health transitions. It schedules periodic heartbeat health checks and fires node-state events.

Important APIs and types: Important methods include `addNode`, `updateNode`, `updateLastHeartbeatTime`, `updateLastKnownLayoutVersion`, `getNode`, `getNodeStatus`, filtered `getNodes` and count methods, `setNodeOperationalState`, `addPipeline`, `removePipeline`, `addContainer`, `removeContainer`, `getContainers`, `run`, `checkNodesHealth`, `forceNodesToHealthyReadOnly`, `pause`, `unpause`, and `close`. It uses `NodeStateMap`, `Node2PipelineMap`, `DatanodeInfo`, `NodeStatus`, `StateMachine<NodeState, NodeLifeCycleEvent>`, `LayoutVersionManager`, `SCMContext`, and SCM events.

Control flow: Construction validates heartbeat/stale/dead intervals, builds a state machine for `HEALTHY`, `HEALTHY_READONLY`, `STALE`, and `DEAD`, defines layout-match/mismatch predicates, creates a scheduled executor, and schedules the first check. `checkNodesHealth` calculates healthy and stale deadlines, scans all nodes, and applies timeout, restore, resurrect, layout mismatch, and layout match transitions. Each state transition updates `NodeStateMap` and fires the mapped event. `run` skips one iteration after long scheduler delays to avoid misclassifying nodes after pauses, otherwise checks health and reschedules itself.

State and persistence behavior: All node maps, pipeline maps, and container membership are in-memory. Datanode operational state is copied from datanode persisted state at registration, and updates through `setNodeOperationalState` must be sent to datanodes elsewhere. Layout version state is based on last heartbeat/report values and finalization checkpoint. The manager does not write its own DB records.

Dependencies and integration points: It drives `STALE_NODE`, `DEAD_NODE`, `HEALTHY_READONLY_NODE`, and `HEALTHY_READONLY_TO_HEALTHY_NODE` handlers. It feeds `NodeManager` implementations, decommission manager, pipeline manager, placement policies, upgrade finalization, and container tracking.

Risks: Snapshot getters are explicitly stale and can be inconsistent across calls. Health processing is synchronized only for check/finalization coordination; maps must preserve their own safety. A long JVM pause skips only one check. `setNodeOperationalState` fires an event based on current health to let other subsystems reconcile operational-state changes, so event handlers must be idempotent.

Test signals: Tests should cover interval validation, all health state-machine transitions, layout mismatch/match behavior, forced readonly finalization, skip-after-delay, event firing for health and operational changes, container/pipeline map updates, registration with persisted op state and expiry, close/pause/unpause behavior, and stale snapshot semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeStateManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeStatus.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeStatus.java

Purpose: `NodeStatus` is an immutable value object combining datanode health (`NodeState`), operational state (`NodeOperationalState`), and optional operational-state expiry time used by maintenance mode.

Important APIs and types: Important APIs include `valueOf`, static sets `maintenanceStates`, `decommissionStates`, `outOfServiceStates`, status constants such as `inServiceHealthy`, `newNodeState`, `newOperationalState`, predicate methods such as `isNodeWritable`, `isDecommission`, `isMaintenance`, `isHealthy`, `isAlive`, `isDead`, `operationalStateExpired`, and value methods `equals`, `hashCode`, `toString`.

Control flow: `valueOf` returns cached singleton instances for expiry-zero combinations and creates a new object when expiry is non-zero. Predicate methods classify operational and health states using immutable enum sets. Expiry compares current wall-clock milliseconds to expiry epoch seconds.

State and persistence behavior: Instances are immutable and carry no external state. They model state that may be persisted by datanodes, but this class does not persist it. Singleton caching reduces allocations for common non-expiring states.

Dependencies and integration points: `NodeStateManager`, `NodeStateMap`, decommission/maintenance workflows, placement policies, and node-count APIs all use `NodeStatus` as the compact state filter and transition value.

Risks: `isAlive` returns true for `HEALTHY` and `STALE`, but not `HEALTHY_READONLY`, while `isHealthy` includes `HEALTHY_READONLY`; callers must choose carefully. `operationalStateExpired` uses wall-clock time, while heartbeat health uses monotonic time. Adding new enum values requires reviewing cached maps and predicate sets.

Test signals: Tests should cover cached identity for zero expiry, new instance for non-zero expiry, all predicate classifications, expiry boundary behavior, equality/hash including expiry, writable definition, and `toString` format.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/PendingContainerTracker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/PendingContainerTracker.java

Purpose: `PendingContainerTracker` prevents SCM from over-allocating containers to a datanode before that datanode reports the new containers in heartbeat reports. It records pending allocations per datanode using a two-window tumbling bucket.

Important APIs and types: Public APIs are `checkSpaceAndRecordAllocation`, `removePendingAllocation`, and visible `getMetrics`. The nested `TwoWindowBucket` exposes synchronized rolling, containment, removal, count, and `checkSpaceAndAdd` logic. It uses `DatanodeInfo`, `ContainerID`, `StorageReportProto`, `VolumeUsage.getUsableSpace`, and `SCMNodeMetrics`.

Control flow: Each datanode owns a `TwoWindowBucket`. Calling `checkSpaceAndRecordAllocation` validates inputs, rejects missing storage reports, rolls the bucket through `DatanodeInfo.getPendingContainerAllocations`, and atomically checks whether usable disk-space-derived container slots exceed current pending count. If so it adds the container to the current window and increments added metrics; otherwise it increments skipped-full-node metrics. Confirmed containers are removed from both windows.

State and persistence behavior: Pending allocation state is in-memory and ages automatically. A single roll moves current allocations to previous and clears current; two elapsed intervals drop both windows. State is not persisted across SCM restart, which is acceptable because datanode reports reestablish actual container state.

Dependencies and integration points: `NodeManager.checkSpaceAndRecordAllocation` and placement/container allocation paths use this tracker. Metrics are shared with SCM node metrics. `DatanodeInfo` owns the per-node bucket so allocation and report state live together.

Risks: Capacity is approximated as usable space divided by max container size; it does not model partial reservations or per-volume placement constraints beyond usable bytes. If reports are stale or empty, allocation is rejected. The two-window aging window trades correctness for eventual cleanup; unreported allocations can disappear after two intervals and allow new allocations.

Test signals: Tests should cover empty reports returning false, add/remove metric increments, per-volume usable-space aggregation, duplicate container additions, single and double roll behavior, removal from both windows, and concurrent check-and-add atomicity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/PendingContainerTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/ReadOnlyHealthyToHealthyNodeHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/ReadOnlyHealthyToHealthyNodeHandler.java

Purpose: `ReadOnlyHealthyToHealthyNodeHandler` handles transitions from `HEALTHY_READONLY` back to `HEALTHY`, typically after a datanode has finalized and its layout versions match SCM again.

Important APIs and types: It implements `EventHandler<DatanodeDetails>` and depends on `SCMServiceManager` plus `SCMService.Event.UNHEALTHY_TO_HEALTHY_NODE_HANDLER_TRIGGERED`.

Control flow: On event, it logs the transition and notifies the service manager that the healthy transition handler has fired. It does not mutate node, pipeline, or container state directly.

State and persistence behavior: The handler has no mutable state beyond its service-manager reference. State transitions have already been applied by `NodeStateManager` before the event is handled.

Dependencies and integration points: It connects upgrade/layout health recovery to SCM service lifecycle notifications. Services waiting for healthy-node transitions can use the notification to re-evaluate readiness or resume work.

Risks: The event name says "UNHEALTHY_TO_HEALTHY" even though the specific transition is readonly-to-healthy, so consumers must understand the broader service event semantics. No exception handling is present around service notification.

Test signals: Tests should verify that the service event is emitted exactly once per handler invocation and that no other managers are touched.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/ReadOnlyHealthyToHealthyNodeHandler.java -->

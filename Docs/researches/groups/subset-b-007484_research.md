<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminDefaultMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminDefaultMonitor.java

## Purpose

`DatanodeAdminDefaultMonitor` is the default periodic monitor used by `DatanodeAdminManager` to advance datanodes through decommission and maintenance states. It checks whether nodes in `DECOMMISSION_INPROGRESS` or `ENTERING_MAINTENANCE` have enough reliable block redundancy to transition to `DECOMMISSIONED` or `IN_MAINTENANCE`. It also keeps `IN_MAINTENANCE` nodes tracked until their maintenance windows expire.

## Important APIs, Types, and State

The core state is `outOfServiceNodeBlocks`, a `TreeMap<DatanodeDescriptor, AbstractList<BlockInfo>>`. A `null` value means a newly tracked node has not yet received its initial full block scan. A non-null value stores a shrinking copy of blocks that were insufficiently stored during earlier checks. `numBlocksPerCheck`, `numBlocksChecked`, `numBlocksCheckedPerLock`, and `numNodesChecked` bound per-tick work under the NameNode write lock. `iterkey` drives `CyclicIteration` so successive ticks resume fairly across tracked nodes.

Public monitor methods implement `DatanodeAdminMonitorInterface`: `run()`, `stopTrackingNode()`, `getTrackedNodeCount()`, `getNumNodesChecked()`, and no-op pending-replication tuning methods. Private control helpers include `processPendingNodes()`, `processCancelledNodes()`, `check()`, `handleInsufficientlyStored()`, `pruneReliableBlocks()`, and `processBlocksInternal()`.

## Control Flow

`run()` exits if the namesystem is not running, resets counters, takes the global namesystem write lock, drains cancelled nodes, admits pending nodes up to `maxConcurrentTrackedNodes`, and calls `check()`. `check()` cycles through tracked nodes until the block budget is exhausted. New nodes get a full scan via `handleInsufficientlyStored()`. Existing nodes run `pruneReliableBlocks()` on the saved insufficient list. If the list becomes empty, the monitor performs another full scan against the live block map before changing administrative state, because the saved list is intentionally stale with respect to block reports and file deletion.

`processBlocksInternal()` is the important block-level loop. It skips deleted blocks and orphan blocks, counts current replicas through `BlockManager`, schedules needed reconstruction if queues are active, asks `DatanodeAdminManager.isSufficient()` whether the block still blocks the admin transition, and updates `LeavingServiceStatus` counters for low-redundancy open files, all low-redundancy blocks, and out-of-service-only replicas. During pruning passes it can temporarily release and reacquire the global write lock after a configured number of blocks to avoid monopolizing the NameNode lock.

## State and Persistence Behavior

The monitor itself is in-memory only. Persistent administrative intent comes from host configuration and `DatanodeDescriptor` admin state; block state lives in `BlockManager` structures. The `outOfServiceNodeBlocks` map is a performance cache and correctness aid, not durable state. It is rebuilt by re-adding nodes after restart or refresh. Maintenance expiry is checked each tick, and expired maintenance is stopped through `DatanodeAdminManager.stopMaintenance()`.

## Dependencies and Integration Points

This class depends tightly on `Namesystem` locking, `BlockManager` replica accounting/reconstruction queues, `DatanodeAdminManager` transition rules, `DatanodeDescriptor` block iterators and leaving-service status, `INode`/`INodeFile` for open-file accounting, and `DFSConfigKeys` for monitor limits. It integrates with `DatanodeAdminMonitorBase` for pending/cancelled queues and reconstruction scheduling.

## Risks and Edge Cases

Risk centers on lock duration, stale cached insufficient block lists, and dead or unhealthy nodes. The full re-scan before final transition is the main safety backstop. Full scans intentionally do not yield the lock because datanode block iterators can otherwise be concurrently modified. Unhealthy nodes can be requeued when the concurrent tracking limit is saturated, preventing dead decommissioning nodes from occupying all monitor slots. Interrupts during lock-yield sleep abort the current pruning pass, delaying but not completing transitions.

## Test Signals

Relevant tests include `TestDatanodeAdminMonitorBase`, `TestDecommission`, `TestDecommissionWithStriped`, `TestMaintenanceState`, `TestMaintenanceWithStriped`, `TestDecommissioningStatus`, and reconstruction tests such as `TestReconstructStripedBlocksWithRackAwareness`. Good regression coverage should assert state transitions, maintenance expiry, requeueing of unhealthy nodes, low-redundancy status counters, and bounded lock/block processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminDefaultMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminManager.java

## Purpose

`DatanodeAdminManager` owns the NameNode-side lifecycle for datanode decommission and maintenance. It starts a configurable monitor implementation, transitions node admin state, adjusts cluster statistics/topology, and defines the redundancy thresholds used by monitors before a node can leave service safely.

## Important APIs, Types, and State

The manager holds references to `Namesystem`, `BlockManager`, `HeartbeatManager`, a single-threaded `ScheduledExecutorService`, and a `DatanodeAdminMonitorInterface` instance. `activate(Configuration)` reflects the monitor class from `DFSConfigKeys.DFS_NAMENODE_DECOMMISSION_MONITOR_CLASS`, injects dependencies into it, and schedules it with fixed delay. `close()` stops the executor.

Administrative entry points are `startDecommission()`, `stopDecommission()`, `startMaintenance()`, and `stopMaintenance()`. Monitor-facing transitions are `setDecommissioned()` and `setInMaintenance()`. The important policy method is `isSufficient(BlockInfo, BlockCollection, NumberReplicas, boolean, boolean)`, which decides when a block no longer blocks decommission or maintenance.

## Control Flow

Starting decommission delegates first to `HeartbeatManager.startDecommission()`, then marks the node in network topology as decommissioning. Dead nodes can become decommissioned immediately inside the heartbeat manager; live nodes get start-time metadata and are queued in the monitor. Stopping decommission reverses heartbeat stats and topology, processes extra redundancy if the node is live, and removes the node from monitor tracking.

Maintenance has parallel flow but with different semantics. `startMaintenance()` always updates the expiration time. Live nodes may move to `ENTERING_MAINTENANCE` unless the minimum maintenance replication threshold is zero or the node is already decommissioned, in which case they enter maintenance immediately. `stopMaintenance()` removes or reprocesses blocks depending on liveness: dead maintenance nodes have associated blocks removed from maps to trigger replication, while live nodes run extra-redundancy processing.

`isSufficient()` first accepts blocks with enough effective replicas. For decommission, under-construction last blocks require minimum storage; closed or non-last blocks can pass with default storage count even if expected redundancy is higher. For maintenance, the threshold is `BlockManager.getMinMaintenanceStorageNum()`.

## State and Persistence Behavior

The manager itself stores only runtime monitor/executor state. Durable intent is supplied externally by host includes/excludes or combined host metadata through `DatanodeManager.refreshDatanodes()` and registration handling. It mutates `DatanodeDescriptor` admin states, leaving-service start time, maintenance expiry, and network topology membership. The executor is daemon-backed and not persisted.

## Dependencies and Integration Points

It is called by `DatanodeManager` during registration and host refresh. It depends on `HeartbeatManager` to keep aggregate stats correct across admin-state changes, `BlockManager` for redundancy policy and block cleanup, `NetworkTopology` for decommission/recommission effects, and monitor implementations for periodic progress.

## Risks and Edge Cases

The safety-critical risk is classifying a block as sufficient too early. The method intentionally distinguishes full expected redundancy, default redundancy during decommission, minimum storage for under-construction last blocks, and the relaxed maintenance minimum. Dead decommissioning nodes do not automatically complete in the monitor path, which avoids durability loss for singly replicated blocks. Maintenance stop for dead nodes is also sensitive because replicas were not removed while the node was in maintenance.

## Test Signals

Useful tests are `TestDecommission`, `TestDecommissionWithStriped`, `TestMaintenanceState`, `TestMaintenanceWithStriped`, `TestDecommissioningStatus`, `TestDatanodeAdminMonitorBase`, and reconfiguration tests that refresh monitor limits. Assertions should cover dead-node immediate transitions, live-node monitor tracking, maintenance expiry, replication sufficiency for open files, and extra-redundancy processing on recommission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminMonitorBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminMonitorBase.java

## Purpose

`DatanodeAdminMonitorBase` is the shared base for decommission and maintenance monitor implementations. It centralizes dependency injection, configuration handling, pending/cancelled node queues, concurrent tracking limits, unhealthy-node requeue policy, and scheduling of reconstruction work for blocks on nodes leaving service.

## Important APIs, Types, and State

The class implements both `DatanodeAdminMonitorInterface` and Hadoop `Configurable`. Injected dependencies are `BlockManager`, `Namesystem`, and `DatanodeAdminManager`. `pendingNodes` is a priority queue sorted by last heartbeat descending so healthier/recently updated nodes are prioritized. `cancelledNodes` is an `ArrayDeque` drained by concrete monitors. `maxConcurrentTrackedNodes` comes from `DFS_NAMENODE_DECOMMISSION_MAX_CONCURRENT_TRACKED_NODES`; zero means no limit.

Important methods are `setConf()`, `startTrackingNode()`, `getPendingNodeCount()`, `getPendingNodes()`, `getCancelledNodes()`, `getUnhealthyNodesToRequeue()`, and `addReconstructionBlockIfNeeded()`.

## Control Flow

Concrete monitor construction flows through `ReflectionUtils`, which calls `setConf()`. This reads the concurrent tracking limit, normalizes negative values to the default, and then invokes subclass-specific `processConf()`. `startTrackingNode()` places nodes into `pendingNodes`; the default monitor later promotes them into its tracked map. `stopTrackingNode()` is subclass-specific because concrete monitors own their tracked-node structure.

`getUnhealthyNodesToRequeue()` is used when the number of nodes needing decommission exceeds `maxConcurrentTrackedNodes`. It computes how many unhealthy tracked nodes should be evicted back to pending and sorts unhealthy nodes so nodes that have been unhealthy longest are requeued first. `addReconstructionBlockIfNeeded()` asks `BlockManager` whether a block needs reconstruction for decommission or maintenance and inserts it into `neededReconstruction` only if it is not already needed or pending and replication queues are being populated.

## State and Persistence Behavior

All queues are in-memory runtime state. The base class does not persist admin operations; it tracks execution backlog derived from `DatanodeDescriptor` admin states and host configuration. Queue order uses `DatanodeDescriptor.getLastUpdate()`, so restart or re-registration changes scheduling priorities indirectly.

## Dependencies and Integration Points

The base class is used by `DatanodeAdminDefaultMonitor` and any configured replacement monitor. It integrates with `BlockManager.neededReconstruction`, `pendingReconstruction`, and reconstruction predicates, and with `DFSConfigKeys` for monitor limits.

## Risks and Edge Cases

The queue comparator favors recent heartbeats; if last-update timestamps are stale or reset unexpectedly, monitor fairness can change. `addReconstructionBlockIfNeeded()` is deliberately conservative about duplicate reconstruction scheduling. Custom monitor implementations must drain `cancelledNodes` under the NameNode lock and honor the base queue semantics to avoid tracking cancelled nodes indefinitely.

## Test Signals

`TestDatanodeAdminMonitorBase` is the direct signal for requeue ordering and configuration behavior. Decommission and maintenance integration tests validate that pending nodes are eventually tracked and that unhealthy decommissioning nodes do not block healthy nodes when concurrency is constrained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminMonitorBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminMonitorInterface.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminMonitorInterface.java

## Purpose

`DatanodeAdminMonitorInterface` defines the pluggable contract for NameNode datanode decommission and maintenance monitors. `DatanodeAdminManager` instantiates implementations reflectively and schedules them as background `Runnable`s.

## Important APIs and Types

The interface extends `Runnable`. It exposes lifecycle methods `startTrackingNode(DatanodeDescriptor)` and `stopTrackingNode(DatanodeDescriptor)`, metrics/accessors `getPendingNodeCount()`, `getTrackedNodeCount()`, `getNumNodesChecked()`, `getPendingNodes()`, and `getCancelledNodes()`, dependency setters for `BlockManager`, `DatanodeAdminManager`, and `Namesystem`, plus tuning accessors for pending replication limits and blocks-per-lock.

## Control Flow

The manager creates the monitor class, calls the dependency setters, and schedules `run()` repeatedly. Admin operations enqueue nodes through `startTrackingNode()` and cancel through `stopTrackingNode()`. The concrete monitor owns how pending/cancelled queues become active checks and how it reports progress.

## State and Persistence Behavior

The interface itself is stateless. Implementations are expected to keep runtime-only queues and counters. The authoritative admin state remains on `DatanodeDescriptor` and host configuration.

## Dependencies and Integration Points

It couples monitor implementations to `BlockManager`, `DatanodeAdminManager`, and `Namesystem` without requiring a specific class. The default implementation also implements Hadoop `Configurable` through `DatanodeAdminMonitorBase`, but the interface does not require that directly.

## Risks and Edge Cases

Because implementations are configurable, compatibility risk is in semantic expectations rather than type signatures: `stopTrackingNode()` must handle cancellation, `run()` must respect NameNode locking and liveness, and tuning setters should validate or no-op consistently. The default monitor returns zero/no-op for tuning knobs it does not support.

## Test Signals

Coverage comes indirectly from monitor instantiation tests, `DatanodeAdminManager` activation paths, `TestDatanodeAdminMonitorBase`, and decommission/maintenance integration suites that exercise the interface through the default implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminMonitorInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeDescriptor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeDescriptor.java

## Purpose

`DatanodeDescriptor` extends client-visible `DatanodeInfo` with NameNode-private, ephemeral state: storage membership, block lists, heartbeat-derived capacity, admin status, queued commands, cache directives, volume failure state, and scheduling counters. It is the central in-memory object used by block management, heartbeat handling, block placement, decommission, maintenance, cache management, and reports.

## Important APIs, Types, and State

Nested `BlockTargetPair` represents a block plus target storages for transfer commands. `BlockQueue<E>` is a synchronized FIFO used for replication, EC replication, EC reconstruction, and lease recovery work. `CachedBlocksList` is an intrusive list for pending cached, cached, and pending uncached block state. `LeavingServiceStatus` stores decommission/maintenance counters: low-redundancy blocks, low-redundancy open files, open file IDs, out-of-service-only replicas, and start time.

Important fields include `storageMap` keyed by storage ID, per-node work queues (`replicateBlocks`, `ecBlocksToBeReplicated`, `ecBlocksToBeErasureCoded`, `recoverBlocks`, `invalidateBlocks`), approximate scheduled-block counters split into current/previous windows by storage type, `isAlive`, `needKeyUpdate`, `forceRegistration`, `disallowed`, `heartbeatedSinceRegistration`, `volumeFailures`, `volumeFailureSummary`, and `numVolumesAvailable`.

Key methods include `updateHeartbeat()`, `updateHeartbeatState()`, `updateStorageStats()`, `updateStorage(DatanodeStorage)`, `injectStorage()`, `pruneStorageMap()`, `getBlockIterator()`, `addBlockToBeReplicated()`, `addECBlockToBeReplicated()`, `addBlockToBeErasureCoded()`, `addBlockToBeRecovered()`, `addBlocksToBeInvalidated()`, command pollers, `chooseStorage4Block()`, scheduled-block increment/decrement, `updateRegInfo()`, `checkBlockReportReceived()`, and `dumpDatanode()`.

## Control Flow

Registration creates or updates the descriptor through `DatanodeManager`, then heartbeat processing calls `HeartbeatManager.updateHeartbeat()`, which delegates to `BlockManager.updateHeartbeat()` and ultimately descriptor heartbeat update methods. `updateStorageStats()` refreshes capacity, usage, cache, transfer count, volume failure state, storage heartbeats, available volumes, and stale/missing storage detection. If volume failures increased or a node has just registered, missing storages are marked `FAILED`; later `HeartbeatManager.heartbeatCheck()` removes blocks from failed storage.

Block work is enqueued by block-management logic and drained by `DatanodeManager.handleHeartbeat()`. Replication and EC replication queues produce `BlockCommand` transfer work; EC reconstruction queue produces `BlockECReconstructionCommand`; recovery queue produces `BlockRecoveryCommand`; invalidation set is drained into invalidate commands. Cache lists are protected by the FSNamesystem lock and converted to cache/uncache commands.

Storage membership is maintained carefully. `updateStorage()` adds new `DatanodeStorageInfo` objects, updates type/state for compatibility, and notifies `DFSTopologyNodeImpl` parents when storage types appear or disappear. `pruneStorageMap()` removes stale storage entries only when they have no associated blocks, preventing block-map loss before block reports reconcile.

## State and Persistence Behavior

This object is runtime state derived from datanode registration, heartbeats, block reports, and NameNode block maps. It is not persisted directly. Block list links live in `DatanodeStorageInfo` and `BlockInfo`; admin state is inherited from `DatanodeInfo`; command queues are transient and can be cleared on failover or safe-mode events. `markStaleAfterFailover()` on storages and `forceRegistration` prevent unsafe reuse of stale knowledge after failover or registration changes.

## Dependencies and Integration Points

`DatanodeDescriptor` integrates with nearly every block-management component: `DatanodeManager`, `HeartbeatManager`, `BlockManager`, `BlockPlacementPolicy`, `CacheReplicationMonitor`, `DatanodeStorageInfo`, `BlockInfo`, `BlockInfoStriped`, `BlockECReconstructionCommand`, `BlockRecoveryCommand`, and topology classes. It uses `StorageReport` and `VolumeFailureSummary` from datanode protocol messages and exposes storage reports for NameNode reports/MXBeans.

## Risks and Edge Cases

High-risk areas are synchronization boundaries and stale storage/block state. `storageMap` has explicit synchronization; block command queues use synchronized helper queues; invalidations synchronize on `invalidateBlocks`. Capacity accounting ignores `PROVIDED` storage for node-local totals. Duplicate mounts are counted once for non-DFS usage. A storage removed from heartbeats cannot be pruned while it still has blocks, so leaked stale storage entries are possible until block reports or block cleanup complete. Scheduled-block counters are approximate by design and roll every ten minutes.

## Test Signals

Direct tests include `TestDatanodeDescriptor`, `TestNameNodePrunesMissingStorages`, `TestHeartbeatHandling`, `TestBlockReportLease`, `TestProvidedStorageMap`, `TestBlockInfo`, and block placement tests. Integration signals include decommission/maintenance tests for `LeavingServiceStatus`, cache tests for cached lists, and EC tests that verify EC replication/reconstruction command queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeDescriptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeManager.java

## Purpose

`DatanodeManager` is the NameNode's top-level coordinator for datanode membership, registration, host inclusion/exclusion, network topology, liveness policy, heartbeat responses, located-block sorting, slow-node reporting, and admin operations. It owns `HeartbeatManager`, `DatanodeAdminManager`, the datanode descriptor map, host-to-node index, topology object, and cluster load/statistics view used by placement policies.

## Important APIs, Types, and State

Core state includes `datanodeMap` keyed by datanode UUID, `networktopology`, `host2DatanodeMap`, `hostConfigManager`, `heartbeatExpireInterval`, `blockInvalidateLimit`, stale read/write configuration, slow peer/disk trackers, software-version counts, and cached `FSClusterStats`. Constructor configuration wires topology implementation, host provider, DNS-to-switch mapping, heartbeat intervals, stale intervals, invalidation limits, read sorting policy, slow peer/disk tracking, maintenance/decommission manager, and cache directive resend interval.

Public and package-level APIs include `activate()`, `close()`, `registerDatanode()`, `refreshNodes()`, lookup methods, `sortLocatedBlocks()`, `getDatanodeListForReport()`, `handleHeartbeat()`, `handleLifeline()`, `removeDatanode()`, `removeDeadDatanode()`, `startAdminOperationIfNecessary()`, `newFSClusterStats()`, slow peer/disk report accessors, and reconfiguration setters for heartbeat and invalidate limits.

## Control Flow

Registration first normalizes the registering IP/hostname from the RPC remote address when available, rejects unresolved hostnames if configured, injects block keys, checks host inclusion, and resolves conflicts between UUID and transfer address. Existing descriptors are updated in place when possible; replacement nodes with the same storage UUID update registration info, topology, host mapping, upgrade domain, software version counts, heartbeat registration, and admin operations. New descriptors are created, assigned topology/dependencies, added to maps/topology, registered with the block-report lease manager, and counted as live.

`refreshNodes()` reloads host configuration and, under the global write lock, calls `refreshDatanodes()`. Nodes not included are marked disallowed. Included nodes with a non-expired maintenance window start maintenance; excluded nodes start decommission; otherwise maintenance and decommission are stopped. Upgrade domain is refreshed for every node.

`handleHeartbeat()` validates registration/disallowed state, updates heartbeat stats, suppresses work in safe mode, prioritizes lease recovery commands, then builds transfer, EC reconstruction, invalidation, cache, key-update, and balancer-bandwidth commands. Replication work is split approximately by queue mix and max transfer capacity, with a special hard limit path for decommissioning nodes. It also ingests slow peer and slow disk reports.

Located-block sorting first moves inactive/stale/slow nodes toward the end, then sorts active replicas by network distance or shuffles them if random ordering is enabled. Striped sorting preserves block-index and token alignment after location reordering.

## State and Persistence Behavior

`DatanodeManager` state is in-memory and reconstructed from registration, host files/providers, and block reports. Host include/exclude and combined host providers persist desired membership/admin metadata externally. `datanodeMap` intentionally tracks all storages ever registered until safe removal; physical map wipe happens when a node restarts with a different storage ID or conflict resolution requires it. Slow peer collection uses a daemon and static concurrent UUID set.

## Dependencies and Integration Points

It is a nexus for `BlockManager`, `Namesystem`, `HeartbeatManager`, `DatanodeAdminManager`, `HostConfigManager`, `Host2NodesMap`, `NetworkTopology`/`DFSNetworkTopology`, DNS mappings, block placement policy via `FSClusterStats`, protocol commands, slow peer/disk trackers, and NameNode safe mode. Client-visible reports and located block responses depend on its filtering and sorting behavior.

## Risks and Edge Cases

Key risks include registration conflict handling, topology resolution failure, stale host include/exclude state, unsafe command delivery during safe mode, and preserving striped block token/index alignment while sorting. The heartbeat response path must not drain queued work in safe mode. Dead maintenance nodes are removed with optional block-map behavior depending on admin state. The `isSlowPeerCollectorInitialized()` method returns `slowPeerCollectorDaemon == null`, which reads like an inverted test name and is worth checking before reuse.

## Test Signals

Direct tests include `TestDatanodeManager`, `TestHeartbeatHandling`, `TestDataNodeLifeline`, `TestSortLocatedBlock`, `TestSortLocatedStripedBlock`, `TestReplicationPolicyExcludeSlowNodes`, `TestSlowPeerTracker`, `TestSlowDiskTracker`, `TestHostFileManager`, `TestHostsFiles`, and decommission/maintenance suites. Regression coverage should exercise registration replacement, disallowed nodes, host refresh transitions, safe-mode heartbeat behavior, slow-node ordering, and invalidation limits derived from heartbeat interval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStatistics.java

## Purpose

`DatanodeStatistics` is the interface exposing aggregate datanode capacity, cache, load, liveness, and storage-tier statistics to NameNode block-management users. `HeartbeatManager` implements it by delegating to `DatanodeStats`.

## Important APIs and Types

The interface provides totals for capacity, DFS used, non-DFS used, remaining space, block-pool used space, cache capacity/usage, xceiver load, in-service xceiver and volume counts, number of in-service datanodes, expired heartbeats, storage-type stats, provided capacity, and a `ClientProtocol#getStats()` compatible `long[]`.

## Control Flow

Consumers obtain an instance through `DatanodeManager.getDatanodeStatistics()`, which returns `HeartbeatManager`. Heartbeat updates mutate `DatanodeStats`; callers read through this interface for reports, metrics, block placement, and client protocol responses.

## State and Persistence Behavior

The interface is stateless. Implementations expose runtime aggregate state derived from live datanode registrations and heartbeats. No values are persisted by the interface.

## Dependencies and Integration Points

It references `StorageType`, `StorageTypeStats`, and `ClientProtocol`. It is the stable boundary between heartbeat/stat aggregation and NameNode consumers such as metrics, reports, and placement policies.

## Risks and Edge Cases

The contract distinguishes total cluster capacity from in-service-only load. Implementations must keep decommissioning, decommissioned, and maintenance states consistent with caller expectations, especially because block placement should not treat out-of-service capacity as writable.

## Test Signals

Capacity and metrics tests such as `TestNamenodeCapacityReport`, `TestBlockStatsMXBean`, `TestNameNodeMetrics`, and `TestHeartbeatHandling` indirectly validate this interface. Tests should confirm percent calculations with zero capacity and correct inclusion/exclusion of decommissioning or maintenance nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStats.java

## Purpose

`DatanodeStats` is the synchronized aggregate implementation behind `HeartbeatManager` statistics. It keeps cluster-wide totals for capacity, usage, cache, xceiver load, in-service counts, expired heartbeats, and per-storage-type statistics.

## Important APIs, Types, and State

Fields track `capacityTotal`, `capacityUsed`, `capacityUsedNonDfs`, `capacityRemaining`, `blockPoolUsed`, `xceiverCount`, `cacheCapacity`, `cacheUsed`, `nodesInService`, `nodesInServiceXceiverCount`, `nodesInServiceAvailableVolumeCount`, and `expiredHeartbeats`. `StorageTypeStatsMap` maintains an `EnumMap<StorageType, StorageTypeStats>` and separates adding/subtracting storage capacity from adding/subtracting node counts by storage type.

Package-private synchronized methods include `add(DatanodeDescriptor)`, `subtract(DatanodeDescriptor)`, getters, percent helpers, and `incrExpiredHeartbeats()`.

## Control Flow

`HeartbeatManager` subtracts a node's old contribution, updates descriptor heartbeat state through `BlockManager`, and adds the updated contribution. `add()` counts xceivers for all live nodes, counts capacity and cache fully only for in-service nodes, and counts cache capacity/used for decommission-in-progress or entering-maintenance nodes. Failed storages are excluded from storage-type stats. For each distinct storage type on a node, node count is updated once even if the node has multiple storages of that type.

## State and Persistence Behavior

All data is in-memory runtime aggregation and is recalculated incrementally. The class does not persist state or rebuild from disk itself; correctness depends on balanced `add()`/`subtract()` calls around liveness and heartbeat transitions.

## Dependencies and Integration Points

It depends on `DatanodeDescriptor`, `DatanodeStorageInfo`, `DatanodeStorage.State`, `StorageType`, `StorageTypeStats`, and `DFSUtilClient` percent helpers. `HeartbeatManager` is the sole implementation-facing owner.

## Risks and Edge Cases

The main risk is imbalance between `add()` and `subtract()`, which would corrupt totals. Administrative state affects accounting: decommissioned nodes do not contribute writable capacity, while decommissioning/entering-maintenance nodes still contribute cache stats. Storage-type node counts require distinct storage type tracking to avoid overcounting a node with multiple volumes of the same type.

## Test Signals

`TestHeartbeatHandling`, `TestBlockStatsMXBean`, `TestNamenodeCapacityReport`, `TestNameNodeMetrics`, and storage policy/placement tests should reveal incorrect aggregate totals. Unit-style tests should verify add/subtract symmetry and storage-type stats removal when the last in-service node of a type is subtracted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStorageInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStorageInfo.java

## Purpose

`DatanodeStorageInfo` represents one storage volume reported by a datanode. It stores storage identity, type, state, capacity metrics, block-list membership, and block-report freshness flags. It is the link between `DatanodeDescriptor` and `BlockInfo` storage lists.

## Important APIs, Types, and State

Static conversion helpers produce datanode arrays, descriptor arrays, storage IDs, and storage types from storage arrays/lists. Instance state includes parent `DatanodeDescriptor`, `storageID`, `storageType`, `state`, capacity/usage metrics, `blockList` head, `numBlocks`, block-report count, `hasReceivedBlockReport`, `heartbeatedSinceFailover`, and `blockContentsStale`.

Important methods include `receivedHeartbeat()`, `receivedBlockReport()`, `markStaleAfterFailover()`, `addBlock()`, `removeBlock()`, `insertToList()`, `getBlockIterator()`, `moveBlockToHead()`, `updateState()`, `toStorageReport()`, and scheduled-block increment/decrement helpers.

## Control Flow

Heartbeats update storage state and metrics and mark `heartbeatedSinceFailover`. A block report clears `blockContentsStale` only after a heartbeat has occurred since failover, then increments block-report count. `addBlock()` handles the case where a block is already associated with a different storage on the same datanode by removing it from the old storage and returning `REPLACED`; if already on this storage, it returns `ALREADY_EXIST`. Otherwise it attaches the block to the head of the storage's linked block list.

`removeBlock()` removes the block from both the linked list and the block's storage membership, decrementing `numBlocks` only when storage removal succeeds. `BlockIterator` traverses the per-storage linked list through `BlockInfo` next pointers.

## State and Persistence Behavior

The object is in-memory state reconstructed from datanode storage reports and block reports. `blockContentsStale` protects invalidation safety after startup/failover: while stale, replicas on the storage should not be trusted for deletion decisions. Capacity metrics mirror the most recent `StorageReport`.

## Dependencies and Integration Points

It integrates with `DatanodeDescriptor`, `BlockInfo`, `DatanodeStorage`, `StorageReport`, storage policies, block placement, heartbeat handling, and invalidation/reconstruction flows. `BlockManager` and block-report processing rely on accurate block list membership.

## Risks and Edge Cases

Block-list consistency is critical. Moving a block between storages on the same datanode must remove old membership before insertion. Failed storage can still contain blocks until heartbeat checks remove associated blocks. Stale-after-failover logic must not be bypassed, or invalidations may delete replicas whose state the NameNode has not yet revalidated.

## Test Signals

Relevant tests include `TestDatanodeDescriptor`, `TestBlockInfo`, `TestNameNodePrunesMissingStorages`, `TestBlockReportLease`, `TestProvidedStorageMap`, and block report variation tests. Good coverage verifies replacement between storages, stale content flags across failover, failed storage block removal, and storage report conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStorageInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ErasureCodingWork.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ErasureCodingWork.java

## Purpose

`ErasureCodingWork` is a `BlockReconstructionWork` specialization that chooses targets and enqueues datanode work for striped erasure-coded blocks. It handles full decode/reconstruction and optimized simple replication of an internal block when all internal blocks exist but rack placement or leaving-service requirements require another copy.

## Important APIs, Types, and State

Constructor state includes `blockPoolId`, `liveBlockIndices`, `liveBusyBlockIndices`, and `excludeReconstructedIndices`, in addition to base reconstruction work state such as block, source nodes, containing nodes, live replica storages, priority, and required additional replicas. Methods include `chooseTargets()`, `addTaskToDatanode()`, `hasAllInternalBlocks()`, `chooseSource4SimpleReplication()`, `createReplicationWork()`, and `findLeavingServiceSources()`.

## Control Flow

`chooseTargets()` delegates to `BlockPlacementPolicy.chooseTarget()` unless the block is marked deleted (`NO_ACK`-style deletion), in which case no targets are chosen. `addTaskToDatanode()` decides which command to enqueue after targets are set. If the block lacks rack diversity but all internal blocks are present, it chooses a source from the rack with the most source nodes and enqueues EC internal-block replication to the source datanode. If decommissioning or live entering-maintenance replicas exist and all internal blocks are present, it finds leaving-service sources whose internal block index is not already present on an in-service source and replicates those internal blocks to targets. Otherwise it sends a full `BlockECReconstructionInfo` task to the first target datanode.

`createReplicationWork()` computes the internal block length with `StripedBlockUtil`, creates a block ID offset by the internal block index, and enqueues it through `DatanodeDescriptor.addECBlockToBeReplicated()`.

## State and Persistence Behavior

This is transient scheduling state created by the reconstruction monitor. It does not persist work itself; it enqueues commands into `DatanodeDescriptor` queues, which are later drained on heartbeat.

## Dependencies and Integration Points

It depends on `BlockPlacementPolicy`, `BlockStoragePolicySuite`, `BlockInfoStriped`, `NumberReplicas`, `StripedBlockUtil`, `DatanodeDescriptor`, and datanode EC reconstruction protocol types. It is part of the block reconstruction pipeline in `BlockManager` and related redundancy monitors.

## Risks and Edge Cases

The critical correctness issue is mapping source node indexes to `liveBlockIndices`. Incorrect index alignment can replicate the wrong internal block. The optimized paths assume all internal blocks are present, including busy blocks for the coverage check. Target count may exceed leaving-service sources, so the code limits to the smaller count and can return false if no source is available.

## Test Signals

Signals include `TestReconstructStripedBlocks`, `TestReconstructStripedBlocksWithRackAwareness`, `TestDecommissionWithStriped`, `TestMaintenanceWithStriped`, `TestErasureCodingCorruption`, and `TestBlockInfoStriped`. Tests should assert rack-only simple replication, decommission/maintenance source selection, deleted-block target suppression, and internal block length/ID calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ErasureCodingWork.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ExcessRedundancyMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ExcessRedundancyMap.java

## Purpose

`ExcessRedundancyMap` tracks block replicas that the NameNode has selected as excess on specific datanodes. It prevents duplicate excess markings and lets block-management code query or remove excess state by datanode UUID and block.

## Important APIs, Types, and State

State is a synchronized `Map<String, LightWeightHashSet<Block>>` keyed by datanode UUID plus an `AtomicLong size` for total excess entries. Methods include `size()`, `clear()`, `contains(DatanodeDescriptor, BlockInfo)`, `add(DatanodeDescriptor, BlockInfo)`, `remove(DatanodeDescriptor, BlockInfo)`, `getExcessRedundancyMap()`, and testing size lookup.

Nested `ExcessBlockInfo` extends `Block` and stores the original `BlockInfo` plus a monotonic timestamp updated at construction or through `setTimeStamp()`.

## Control Flow

`add()` creates a per-datanode set if needed, wraps the block in `ExcessBlockInfo`, and increments total size only if the set did not already contain an equivalent block. `remove()` deletes the block, decrements size, logs the change, and removes the per-datanode set when empty. `contains()` uses block equality in the per-datanode set.

## State and Persistence Behavior

The map is runtime-only. It reflects current excess-replica decisions and is cleared or rebuilt by block-management processing. The timestamp records when an excess decision was made, which can support aging or diagnostics by consumers.

## Dependencies and Integration Points

It integrates with `BlockManager` over-replication handling, `NameNode.blockStateChangeLog`, `LightWeightHashSet`, `DatanodeDescriptor`, and `BlockInfo`. It is thread-safe through synchronized methods even though the size counter is atomic.

## Risks and Edge Cases

The main risk is stale entries after block deletion, replica movement, or datanode removal. Consumers must call `remove()` or `clear()` appropriately. `getExcessRedundancyMap()` exposes the mutable map under synchronization only for the call; external mutation would be risky if used outside trusted package code.

## Test Signals

Over-replication tests such as `TestOverReplicatedBlocks`, `TestBlockManager`, `TestNodeCount`, and pending reconstruction/invalidation tests can reveal incorrect excess tracking. Unit coverage should assert add idempotency, remove cleanup of empty datanode sets, and total size consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ExcessRedundancyMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/FSClusterStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/FSClusterStats.java

## Purpose

`FSClusterStats` is a small placement-facing interface that exposes cluster load, stale-write avoidance, in-service datanode count, average xceiver load, average volume load, and per-storage-type stats. `DatanodeManager.newFSClusterStats()` creates the concrete anonymous implementation backed by `HeartbeatManager`.

## Important APIs and Types

Methods are `getTotalLoad()`, `isAvoidingStaleDataNodesForWrite()`, `getNumDatanodesInService()`, `getInServiceXceiverAverage()`, `getInServiceXceiverAverageForVolume()`, and `getStorageTypeStats()`. It uses `StorageType` and `StorageTypeStats`.

## Control Flow

Block placement policies ask this interface for load and storage-type context when choosing write targets. The implementation computes averages defensively, returning zero when no in-service nodes or volumes are available.

## State and Persistence Behavior

The interface is stateless. Values are runtime views over heartbeat-maintained statistics and stale-node policy.

## Dependencies and Integration Points

Primary consumers are block placement policies such as default, available-space, upgrade-domain, and rack-fault-tolerant policies. `DatanodeManager` mediates stale-write policy and `HeartbeatManager` supplies load and storage stats.

## Risks and Edge Cases

Average load semantics depend on the denominator: node average uses in-service datanode count, while volume average uses writable volume count. If administrative state accounting is wrong, placement may overuse decommissioning, maintenance, stale, or overloaded nodes.

## Test Signals

Signals include `TestReplicationPolicy`, `TestReplicationPolicyConsiderLoad`, `TestReplicationPolicyRatioConsiderLoadWithStorage`, available-space placement tests, and stale-node tests. Coverage should validate zero-denominator behavior and stale-write avoidance toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/FSClusterStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HeartbeatManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HeartbeatManager.java

## Purpose

`HeartbeatManager` owns the live datanode list, heartbeat-derived aggregate statistics, stale-node tracking, dead-node detection, failed-storage detection, and periodic block-key update scheduling. It implements `DatanodeStatistics` for the rest of the NameNode.

## Important APIs, Types, and State

State includes synchronized `datanodes`, `DatanodeStats stats`, `heartbeatRecheckInterval`, daemon `heartbeatThread`, `StopWatch heartbeatStopWatch`, configured batch size for dead/failed storage removal, `Namesystem`, `BlockManager`, stale-node logging flag, and `staleDataNodes`. Public/package methods include `activate()`, `close()`, `register()`, `addDatanode()`, `removeDatanode()`, `updateHeartbeat()`, `updateLifeline()`, `startDecommission()`, `stopDecommission()`, `startMaintenance()`, `stopMaintenance()`, `heartbeatCheck()`, and all `DatanodeStatistics` getters.

## Control Flow

Registration adds live nodes and initializes heartbeat state. Heartbeat updates subtract old stats, delegate heartbeat state updates through `BlockManager`, and add new stats. Lifeline updates intentionally call `updateHeartbeatState()` rather than full heartbeat update so lifelines do not count as the first heartbeat after registration.

Admin methods adjust descriptor state under the heartbeat manager lock while maintaining stats symmetry. Dead nodes can transition immediately to decommissioned or in-maintenance because no live block movement can be commanded.

`heartbeatCheck()` skips startup safe mode, then repeatedly scans live datanodes in bounded batches. It records expired heartbeats, stale nodes, stale storage counts, and failed storages with blocks. Outside the heartbeat-manager synchronized section, it takes the block-manager write lock to remove dead datanodes or remove blocks associated with failed storages. It loops until no dead nodes or failed storages remain in the current pass. The inner daemon checks periodically, marks block-token key updates when needed, sleeps five seconds, and compensates for long pauses by skipping the next scan if the stopwatch indicates an excessive delay.

## State and Persistence Behavior

All state is runtime-only and rebuilt from registrations and heartbeats. `expiredHeartbeats` is a runtime counter. Stale-node sets are diagnostic/control state and are reflected into `DatanodeManager` counters. Failed storage handling mutates block maps through `BlockManager` but the manager itself does not persist data.

## Dependencies and Integration Points

It integrates with `DatanodeManager` for dead-node policy and stale interval, `BlockManager` for heartbeat update and block cleanup, `Namesystem` safe mode and locking, `DatanodeDescriptor` admin/liveness state, and `DatanodeStats` aggregation. `DatanodeAdminManager` relies on it for stats-correct admin transitions.

## Risks and Edge Cases

The dead-node scan must avoid cascading removals during long synchronized sections, hence batch limits and pause detection. Safe mode checks occur both before and after scan staging. Failed storages may receive late incremental block reports, so block removal is centralized here. Lifeline updates must not accidentally mark a node fully heartbeated since registration.

## Test Signals

`TestHeartbeatHandling`, `TestDataNodeLifeline`, `TestDeadDatanode`, `TestDatanodeManager`, `TestNameNodePrunesMissingStorages`, `TestBlockStatsMXBean`, and NameNode metrics tests are relevant. Tests should cover dead detection, stale-node counts/logging, failed storage removal, safe-mode suppression, stats add/subtract symmetry, and excessive-pause scan skipping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HeartbeatManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/Host2NodesMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/Host2NodesMap.java

## Purpose

`Host2NodesMap` indexes datanode descriptors by IP address and hostname for quick lookup during registration, reports, block-location sorting, and slow-peer mapping. It supports the rare case of multiple datanode processes on one host.

## Important APIs, Types, and State

State consists of `mapHost`, mapping hostname to IP address, `map`, mapping IP address to an array of `DatanodeDescriptor`s, and a `ReentrantReadWriteLock`. Methods are `contains()`, `add()`, `remove()`, `getDatanodeByHost()`, `getDatanodeByXferAddr()`, `getDataNodeByHostName()`, and `toString()`.

## Control Flow

`add()` rejects null or already-contained descriptors, stores hostname-to-IP mapping, and appends to the IP array. `remove()` deletes a descriptor by identity, removing the IP and hostname entry when the last descriptor for that IP is gone, or compacting the array otherwise. `getDatanodeByHost()` returns null for no entry, the single descriptor for normal hosts, or a random descriptor when multiple nodes share the IP. `getDatanodeByXferAddr()` disambiguates by transfer port.

## State and Persistence Behavior

The map is runtime-only and mirrors `DatanodeManager.datanodeMap` plus current registration addresses. It is rebuilt by datanode registration and removal.

## Dependencies and Integration Points

`DatanodeManager` uses it for registration conflict detection, block-location sorting client lookup, host reports, slow-peer IP mapping, and descriptor resolution from host entries. Tests use it directly.

## Risks and Edge Cases

The read/write lock is reentrant, so `add()` can call `contains()` while holding the write lock. Hostname mapping removal is simple and may be lossy if multiple hostnames map to the same IP with multiple datanodes; the class assumes the common one-hostname case. Random selection for multiple nodes is acceptable for host-only lookup but should not be used when the transfer port is known.

## Test Signals

`TestHost2NodesMap`, `TestDatanodeManager`, `TestDatanodeRegistration`, and located-block sorting tests are relevant. Coverage should include duplicate add, identity-based remove, multiple datanodes per IP, hostname lookup, and transfer-port lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/Host2NodesMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostConfigManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostConfigManager.java

## Purpose

`HostConfigManager` abstracts how NameNode host membership and administrative intent are loaded. Implementations can use classic include/exclude files or richer combined host files with upgrade domains and maintenance expiration.

## Important APIs and Types

The abstract class implements `Configurable` and defines `getIncludes()`, `getExcludes()`, `isIncluded(DatanodeID)`, `isExcluded(DatanodeID)`, `refresh()`, `getUpgradeDomain(DatanodeID)`, and `getMaintenanceExpirationTimeInMS(DatanodeID)`.

## Control Flow

`DatanodeManager` constructs an implementation from `DFS_NAMENODE_HOSTS_PROVIDER_CLASSNAME_KEY`, calls `refresh()` during startup and host refresh, checks `isIncluded()` during registration and refresh, and uses `isExcluded()` or maintenance expiration to start decommission or maintenance. Upgrade domain is read during registration and refresh.

## State and Persistence Behavior

The abstraction does not define storage. Implementations are responsible for reading and retaining external persistent configuration. `HostFileManager` uses include/exclude files; `CombinedHostFileManager` supports richer metadata.

## Dependencies and Integration Points

It is the membership boundary between external admin configuration and `DatanodeManager`/`DatanodeAdminManager`. It uses `DatanodeID` and `InetSocketAddress` to express datanode identity and host entries.

## Risks and Edge Cases

Implementations must define wildcard-port semantics consistently and resolve hostnames without excessive registration latency. Incorrect `isIncluded()` can reject valid datanodes or allow unexpected ones. Maintenance expiration returning zero means no maintenance support in the classic file implementation.

## Test Signals

`TestHostFileManager`, `TestHostsFiles`, `TestDatanodeManager`, `TestMaintenanceState`, and DFS admin refresh tests are relevant. Tests should validate refresh behavior, include-empty semantics, exclude-driven decommission, upgrade domain propagation, and maintenance expiration interpretation for richer implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostConfigManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostFileManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostFileManager.java

## Purpose

`HostFileManager` is the classic include/exclude-file implementation of `HostConfigManager`. It loads configured host files, canonicalizes entries into resolved `InetSocketAddress` values, and answers whether datanodes are allowed or excluded.

## Important APIs, Types, and State

State includes `Configuration conf`, `HostSet includes`, and `HostSet excludes`. Methods include `setConf()`, `getConf()`, `refresh()`, `readFile()`, `parseEntry()`, `getIncludes()`, `getExcludes()`, `isIncluded()`, `isExcluded()`, `getUpgradeDomain()`, `getMaintenanceExpirationTimeInMS()`, and test-visible `refresh(HostSet, HostSet)`.

## Control Flow

`refresh()` reads `DFS_HOSTS` and `DFS_HOSTS_EXCLUDE`. `readFile()` uses `HostsFileReader` to load unique entries, parses each entry as a URI authority, defaults missing ports to zero, resolves it into an `InetSocketAddress`, and ignores unresolved or malformed entries with warnings. `isIncluded()` treats an empty include set as allow-all; otherwise the datanode's resolved address must match the include set. `isExcluded()` checks the exclude set.

## State and Persistence Behavior

Persistent state lives in external include/exclude files. `HostFileManager` holds synchronized in-memory `HostSet` snapshots and atomically swaps them on refresh. It does not persist upgrade domain or maintenance metadata; both return null/zero.

## Dependencies and Integration Points

`DatanodeManager` uses it by default as the host provider. It depends on `DFSConfigKeys`, `HostsFileReader`, `DatanodeID`, and `HostSet`. The parser's port-zero wildcard behavior must match `HostSet`.

## Risks and Edge Cases

DNS failures at refresh time drop entries. That is deliberate but can surprise operators if a host temporarily fails to resolve. Parsing via URI authority catches host:port syntax, but invalid lines are ignored rather than fatal. Classic host files cannot start maintenance mode or set upgrade domains; operators need the combined host provider for that.

## Test Signals

`TestHostFileManager`, `TestHostsFiles`, `TestDFSAdmin`, and `TestDatanodeRegistration` are primary signals. Tests should cover empty include allow-all behavior, wildcard port matching, unresolved entry warnings, malformed entries, exclude-driven decommission, and refresh swapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostFileManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostSet.java

## Purpose

`HostSet` stores resolved host/port entries and implements the wildcard-port matching semantics used by HDFS include and exclude files. Port `0` represents all datanodes on the host.

## Important APIs, Types, and State

The class wraps a Guava `HashMultimap<InetAddress, Integer>` from host address to ports. Methods are `matchedBy(InetSocketAddress)`, `match(InetSocketAddress)`, `isEmpty()`, `size()`, `add(InetSocketAddress)`, `iterator()`, and `toString()`.

## Control Flow

`add()` logs and ignores unresolved addresses, otherwise stores address and port. `match(addr)` answers whether the set contains either the exact port or wildcard port zero for the address. `matchedBy(addr)` is the opposite partial-order query used when generating dead-node reports: a wildcard query address matches any stored port, while a non-wildcard query requires exact stored port. Iteration returns unmodifiable socket addresses built from entries.

## State and Persistence Behavior

The set is in-memory only and usually held as a snapshot inside `HostFileManager`. It does not perform synchronization; callers use it under higher-level synchronization or as an immutable-after-refresh object.

## Dependencies and Integration Points

`HostFileManager` uses it for includes and excludes. `DatanodeManager.getDatanodeListForReport()` uses `matchedBy()` to avoid synthesizing dead report entries for included hosts already represented by known nodes.

## Risks and Edge Cases

Unresolved addresses are silently not added beyond a warning. The two matching directions are easy to confuse: `match()` means incoming datanode address is covered by a set entry; `matchedBy()` means a known/found address covers an include entry for reporting. Port zero semantics are central to correctness.

## Test Signals

`TestHostSet` and `TestHostFileManager` directly cover this behavior. Tests should cover exact ports, wildcard ports, unresolved add rejection, iterator contents, and `matchedBy()` vs `match()` differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/InvalidateBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/InvalidateBlocks.java

## Purpose

`InvalidateBlocks` tracks blocks that should be deleted from datanodes and batches them into invalidation work sent on heartbeat. It maintains separate queues for contiguous replicated blocks and striped erasure-coded blocks so counts and limits can be managed accurately.

## Important APIs, Types, and State

State includes `nodeToBlocks`, `nodeToECBlocks`, `LongAdder numBlocks`, `LongAdder numECBlocks`, `blockInvalidateLimit`, `BlockIdManager`, `pendingPeriodInMs`, and `startupTime`. Methods include `numBlocks()`, `getBlocks()`, `getECBlocks()`, `contains()`, `add()`, `remove(dn)`, `remove(dn, block)`, `dump()`, `getDatanodes()`, `getInvalidationDelay()`, `invalidateWork(DatanodeDescriptor)`, and `clear()`.

## Control Flow

`add()` selects the replicated or striped map using `BlockIdManager.isStripedBlock()`, creates a per-datanode `LightWeightHashSet` if needed, inserts the block, updates the appropriate counter, and optionally logs. `contains()` verifies block presence and generation stamp equality. `remove()` variants delete all work for a datanode or a specific block, decrement counters, and remove empty per-node entries.

`invalidateWork()` first enforces the startup deletion delay. If the delay has not elapsed, it returns null and logs that deletion is delayed. Otherwise it polls up to `blockInvalidateLimit` replicated blocks first, then uses remaining capacity for EC blocks. If any blocks are selected, it removes empty node entries and enqueues the blocks into the descriptor's invalidate set via `addBlocksToBeInvalidated()`. The actual protocol command is later emitted by `DatanodeManager.handleHeartbeat()`.

## State and Persistence Behavior

Invalidation queues are runtime NameNode state derived from block deletion, over-replication, and block-report reconciliation. They are not persisted here. The startup pending period protects against deleting replicas before stale storage and block reports have been reconciled after NameNode startup.

## Dependencies and Integration Points

It depends on `BlockIdManager`, `DatanodeInfo`, `DatanodeDescriptor`, `LightWeightHashSet`, NameNode block-state logging, and `DFS_NAMENODE_STARTUP_DELAY_BLOCK_DELETION_SEC_KEY`. `BlockManager` computes invalidation work and `DatanodeManager` sends the resulting commands.

## Risks and Edge Cases

Important risks include deleting blocks during startup before block reports establish freshness, generation-stamp mismatches, and starving EC invalidations if replicated invalidations constantly fill the limit. The class is synchronized for map/counter consistency, while `LongAdder` is used for counters. `dump()` can output both maps for metasave diagnostics.

## Test Signals

`TestComputeInvalidateWork`, `TestPendingInvalidateBlock`, `TestPendingDataNodeMessages`, `TestBlockManager`, `TestDeleteRace`, and startup tests are relevant. Coverage should assert startup delay behavior, generation-stamp-aware contains, replicated-before-EC batching, per-node cleanup, and command handoff to `DatanodeDescriptor`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/InvalidateBlocks.java -->

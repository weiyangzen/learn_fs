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

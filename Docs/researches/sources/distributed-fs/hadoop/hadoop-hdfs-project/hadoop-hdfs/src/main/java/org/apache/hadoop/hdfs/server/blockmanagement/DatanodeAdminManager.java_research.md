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

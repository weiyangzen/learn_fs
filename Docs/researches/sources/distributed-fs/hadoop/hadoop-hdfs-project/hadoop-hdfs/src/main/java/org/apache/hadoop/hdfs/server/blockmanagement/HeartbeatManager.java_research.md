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

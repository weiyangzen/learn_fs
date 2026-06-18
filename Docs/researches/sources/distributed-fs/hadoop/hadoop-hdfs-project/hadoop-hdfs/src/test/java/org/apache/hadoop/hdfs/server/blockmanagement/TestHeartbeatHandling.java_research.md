# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHeartbeatHandling.java

## Purpose
`TestHeartbeatHandling` verifies namenode heartbeat handling for replication commands, invalidation commands, block recovery commands, stale-node filtering, and heartbeat-check stopwatch abort behavior.

## Important APIs, Types, and Functions
The test uses `FSNamesystem`, `HeartbeatManager`, `NameNodeAdapter.sendHeartBeat`, `DatanodeDescriptor`, `DatanodeRegistration`, `BlockCommand`, `BlockRecoveryCommand`, `DatanodeProtocol` actions, `BlockInfoContiguous`, and `HeartbeatManager.shouldAbortHeartbeatCheck`.

## Control Flow
`testHeartbeat` starts a cluster, queues more replication and invalidation work than heartbeat limits allow, sends repeated synthetic heartbeats, and verifies command counts and action order as queues drain. `testHeartbeatBlockRecovery` starts three datanodes, creates under-recovery blocks across their storages, manipulates last-update timestamps, and checks which nodes appear in the recovery command. `testHeartbeatStopWatch` creates a mocked heartbeat manager, restarts its stopwatch, sleeps across the configured recheck interval, and checks abort decisions.

## State and Persistence Behavior
State includes per-datanode replication queues, invalidation queues, storage metadata, under-recovery block state, heartbeat timestamps, and the heartbeat manager stopwatch. Cluster state is temporary and scoped to each test.

## Dependencies and Integration Points
The file integrates namenode heartbeat RPC handling through test adapters, block-manager queue limits, datanode storage updates, stale interval logic, and block recovery command construction.

## Risks and Edge Cases
Covered risks include over-large heartbeat command batches, incorrect command ordering, failing to drain remainder queues, including stale nodes unnecessarily in recovery, excluding all nodes when every node appears stale, and heartbeat checks running too long without aborting.

## Test Signals
Assertions verify exact command array lengths, `DNA_TRANSFER`, `DNA_INVALIDATE`, and `DNA_RECOVERBLOCK` actions, exact block counts per command, exact recovery-node arrays for all-alive, one-stale, and all-stale cases, and stopwatch abort decisions before and after the recheck interval.

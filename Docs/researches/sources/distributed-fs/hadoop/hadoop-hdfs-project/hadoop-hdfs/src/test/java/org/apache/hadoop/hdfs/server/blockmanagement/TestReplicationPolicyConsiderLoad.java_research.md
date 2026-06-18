# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyConsiderLoad.java

## Purpose
`TestReplicationPolicyConsiderLoad` verifies that placement policy load filtering uses the correct in-service average and configured load factor. It runs against both default and upgrade-domain policies to ensure load exclusion composes with topology-aware placement.

## Important APIs, types, and functions
The class extends `BaseReplicationPolicyTest`, parameterized over `BlockPlacementPolicyDefault` and `BlockPlacementPolicyWithUpgradeDomain`. Its topology has six DataNodes across three racks. It sets `DFS_NAMENODE_REDUNDANCY_CONSIDERLOAD_FACTOR` to 1.2 and uses `HeartbeatManager.updateHeartbeat` to set xceiver counts. It reads `FSClusterStats.getInServiceXceiverAverage` and invokes `chooseTarget`.

## Control flow
`testChooseTargetWithDecomNodes` sets xceiver counts on three nodes, verifies average load over all six in-service nodes, then marks the first three DataNodes decommissioned. The in-service average is recalculated over the remaining three nodes, and choosing three targets from a decommissioned writer must return the three non-decommissioned storages. `testConsiderLoadFactor` sets different xceiver counts across all six nodes, calculates the average, chooses three targets, and asserts no chosen node exceeds average times 1.2.

## State and persistence behavior
The tested state is volatile heartbeat load, decommission flags, and derived in-service load statistics. Decommissioning is started and force-marked in memory, then stopped in the finally block. No persistent decommission state or fsimage behavior is tested.

## Dependencies and integration points
The tests exercise the placement policy's `isGoodTarget` load checks through DatanodeManager heartbeat stats. They also check that decommissioned DataNodes are excluded from average-load calculations and target eligibility.

## Risks and test signals
Regression signals are incorrect in-service average values, choosing decommissioned nodes, or selecting overloaded nodes above the configured factor. The tests rely on manual heartbeat updates under the BlockManager write lock and reset decommission state after execution.

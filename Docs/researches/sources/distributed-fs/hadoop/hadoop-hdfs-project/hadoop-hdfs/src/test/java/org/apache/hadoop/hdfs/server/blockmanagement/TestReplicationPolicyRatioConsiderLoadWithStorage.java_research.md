# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyRatioConsiderLoadWithStorage.java

## Purpose
`TestReplicationPolicyRatioConsiderLoadWithStorage` validates the load-by-volume placement option. It ensures the default placement policy excludes nodes whose total xceiver load is high and also excludes nodes whose load is too high relative to their number of available volumes.

## Important APIs, types, and functions
The class extends `BaseReplicationPolicyTest` with `BlockPlacementPolicyDefault`. It enables `DFS_NAMENODE_REDUNDANCY_CONSIDERLOAD_KEY`, sets the load factor to 2, and enables `DFS_NAMENODE_REDUNDANCY_CONSIDERLOADBYVOLUME_KEY`. `getDatanodeDescriptors` creates five racks, adds five extra storages to each DataNode, and marks a different number of storages available per node using `DatanodeStorageInfo.setUtilizationForTesting`. `HeartbeatManager.updateHeartbeat` supplies xceiver counts.

## Control flow
The single test updates heartbeats so total cluster load is 200 and average node load is 40. Based on available volume counts, DataNode 1 exceeds node load and DataNode 0 exceeds per-storage load. Choosing three targets from DataNode 2 returns DataNodes 2, 3, and 4. Choosing four targets still returns only those three because the two overloaded nodes remain ineligible.

## State and persistence behavior
State is in-memory storage utilization, available volume count, DataNode xceiver count, and derived average load. The test does not interact with real files or persistence.

## Dependencies and integration points
This test targets placement policy load filtering with the volume-aware extension. It depends on `BlockManagerTestUtil.getStorageReportsForDatanode` reflecting the per-storage utilization injected into descriptors.

## Risks and test signals
The main signals are target length and membership set. It catches regressions where load is considered only per DataNode and not per available volume, or where overloaded nodes are returned to satisfy requested replica count. The comments encode the expected arithmetic and are important for maintaining the thresholds.

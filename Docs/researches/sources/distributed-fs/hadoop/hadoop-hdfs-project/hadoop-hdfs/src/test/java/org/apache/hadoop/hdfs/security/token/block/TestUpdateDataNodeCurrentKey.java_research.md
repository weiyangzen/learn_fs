# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/TestUpdateDataNodeCurrentKey.java

## Purpose
This test verifies that DataNodes receive and retain the current HDFS block-token key from the correct NameNode in an HA topology. It covers standby startup, active NameNode failover, DataNode joins after activation, and standby restart scenarios.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `DFSConfigKeys.DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY`, `DataNode`, `BlockPoolTokenSecretManager`, `BlockKey`, `DatanodeInfo`, and `HdfsConstants.DatanodeReportType.LIVE`. Test methods are `testUpdateDatanodeCurrentKeyWithStandbyNameNodes`, `testUpdateDatanodeCurrentKeyWithFailover`, and `testUpdateDatanodeCurrentKeyFromActiveNameNode`.

## Control Flow
`setup` builds a one-DataNode HA cluster with block access tokens enabled. The standby test reads the block pool ID from NameNode 0 and asserts the DataNode's block-pool token manager already has a non-null current key. The failover test transitions NameNode 0 active, waits briefly for propagation, and compares the active NameNode current key to the DataNode current key. The new-DataNode test activates NameNode 0, starts a second DataNode, confirms two live DataNodes, restarts the standby NameNode, then asserts old and new DataNodes both match the active NameNode current key.

## State and Persistence Behavior
The primary state is cluster-local HA NameNode state, DataNode block-pool token secret manager state, and current `BlockKey` values. Cluster lifecycle is owned by `@BeforeEach` and `@AfterEach`, and `cluster.shutdown()` clears MiniDFSCluster state. The test does not write application files; it relies on block-pool registration, heartbeats, and key update propagation.

## Dependencies and Integration Points
The file integrates HDFS HA MiniDFSCluster startup, NameNode active/standby transitions, DataNode block-pool token managers, NameNode block manager token secret manager, and DataNode live reports. It specifically exercises the NameNode-to-DataNode key distribution path used when block access tokens are enabled.

## Risks and Test Signals
Timing is the main risk: `Thread.sleep(3000)` assumes key propagation has completed after active transition. The duplicate config set for `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY` is harmless but noisy. Test signals are direct non-null and equality checks between active NameNode and DataNode `BlockKey` instances.

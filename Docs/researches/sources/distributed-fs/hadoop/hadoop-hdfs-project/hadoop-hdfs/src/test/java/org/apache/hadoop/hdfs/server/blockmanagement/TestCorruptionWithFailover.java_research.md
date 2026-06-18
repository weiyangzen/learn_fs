# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCorruptionWithFailover.java

## Purpose
`TestCorruptionWithFailover` verifies that corrupt replica accounting survives HA failover for a replicated file when a datanode reports an older-generation replica after pipeline recovery.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster` with `MiniDFSNNTopology.simpleHATopology`, `DistributedFileSystem`, `FSDataOutputStream`, `BlockManager`, `GenericTestUtils.waitFor`, and `DFS_NAMENODE_CORRUPT_BLOCK_DELETE_IMMEDIATELY_ENABLED`.

## Control Flow
The test disables immediate corrupt-block deletion and lowers the write replacement minimum replication. It starts a three-datanode HA cluster, activates NN0, writes and syncs 1 MiB, stops one datanode to trigger pipeline update, writes another 1 MiB, and closes. Both namenodes mark all datanodes stale. The stopped datanode is restarted and eventually reports a lower-generation replica, causing NN0 to count one corrupt block. The test then fails over to NN1 and waits for NN1 to report the same corrupt count.

## State and Persistence Behavior
State under test is HA block-manager corrupt-replica metadata, datanode stale state, and generation-stamp differences created by pipeline recovery. The corrupt replica is not deleted immediately, so its metadata remains visible across failover.

## Dependencies and Integration Points
The test integrates DFS output stream pipeline recovery, datanode restart/reporting, namenode HA transitions, and block-manager corrupt counters.

## Risks and Edge Cases
The scenario guards against active and standby block managers diverging on corrupt counts when stale datanode handling postpones deletion during failover.

## Test Signals
`GenericTestUtils.waitFor` checks `bm0.getCorruptBlocks() == 1`, then after failover checks `bm1.getCorruptBlocks() == 1`.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestErasureCodingCorruption.java

## Purpose
`TestErasureCodingCorruption` verifies that a striped block group is not left in the corrupt replica map when a failed-write internal replica should be deleted but deletion is postponed due to stale datanode handling around failover.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster` with HA topology, `DistributedFileSystem`, `FSDataOutputStream`, `BlockManager.getCorruptECBlockGroups`, `GenericTestUtils.waitFor`, and `DFS_NAMENODE_CORRUPT_BLOCK_DELETE_IMMEDIATELY_ENABLED`.

## Control Flow
The test disables immediate corrupt-replica deletion, starts an eight-datanode HA cluster, activates NN0, creates `/dir`, sets the `RS-6-3-1024k` EC policy, and writes more than one stripe. It stops one datanode to trigger pipeline update, writes more data, and closes the file. NN0 transitions standby then active, the stopped datanode restarts and reports the failed-write replica, and the test waits for the EC corrupt-block-group count to be zero.

## State and Persistence Behavior
State under test includes EC block-group corruption metadata, datanode report processing, generation-stamp mismatch handling, and stale-storage deletion postponement. The file data exists only within the test cluster lifetime.

## Dependencies and Integration Points
The test integrates HDFS EC write pipelines, HA transitions, datanode restart/report logic, corrupt-replica map maintenance, and block-manager EC corrupt counters.

## Risks and Edge Cases
The main edge case is specific to striped blocks: a single bad internal replica can cause the whole block group to be marked corrupt, but if that replica is scheduled for deletion the block group should not remain counted as corrupt indefinitely.

## Test Signals
The final wait condition asserts `bm.getCorruptECBlockGroups() == 0`, proving that the block group was explicitly removed from corrupt EC accounting after the failed-write replica report.

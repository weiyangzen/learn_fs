# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlocksWithNotEnoughRacks.java

## Purpose
`TestBlocksWithNotEnoughRacks` is a slow integration suite for rack-aware replica placement and reconstruction. It verifies that HDFS repairs or preserves rack diversity when blocks are under-replicated, mis-replicated, corrupt, over-replicated, affected by node failure, or affected by decommissioning. It also covers upgrade-domain-aware placement.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DFSTestUtil.waitForReplication`, `NameNodeAdapter.setReplication`, `DatanodeManager.removeDatanode`, `HostsFileWriter`, `BlockPlacementPolicyWithUpgradeDomain`, `BlockManager.neededReconstruction`, and `BlockManager.scheduleReconstruction`. Helpers include `getConf`, `scheduleReconstruction`, and `getDnDescriptors`.

## Control Flow
Cluster configurations use short heartbeat, redundancy, pending-reconstruction, and block-report intervals plus a topology script key to enable rack awareness. Individual tests create files with controlled replication and rack layouts, add or remove datanodes, change replication factors, corrupt replicas, decommission nodes, run `fsck -replicate`, and then wait for expected rack counts and replica counts. Upgrade-domain tests assign `upgradeDomain` values to `DatanodeDescriptor`s and verify additional reconstruction requirements and final placement.

## State and Persistence Behavior
State under test includes namenode block placement metadata, low-redundancy queues, excess/invalidation decisions, datanode admin state, host exclude files, corrupt replica state, and upgrade-domain labels. The tests persist blocks in MiniDFSCluster data directories during each test but clean clusters afterward.

## Dependencies and Integration Points
This file integrates the namenode block manager, rack topology mapping, decommission manager, fsck replication command, datanode liveness removal, corrupt replica processing, and upgrade-domain placement policy.

## Risks and Edge Cases
Covered risks include blocks that are numerically replicated but all on one rack, corruption repair choosing same-rack targets, over-replication deleting the only cross-rack copy, decommissioning reducing rack diversity, and upgrade-domain scheduling needing multiple additional replicas.

## Test Signals
The main signals are `DFSTestUtil.waitForReplication` with expected rack counts, fsck output containing placement-policy violation and queued replication text, byte comparisons for non-corrupt replicas, `BlockReconstructionWork.getAdditionalReplRequired`, and successful waits for both rack and upgrade-domain diversity.

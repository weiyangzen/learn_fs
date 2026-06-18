
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceRackFaultTolerantBPP.java

## Purpose
This class tests `AvailableSpaceRackFaultTolerantBlockPlacementPolicy`, combining available-space preference with rack-fault-tolerant target spread. It verifies policy replacement, probabilistic preference for less-used nodes, null-safe exclusion handling, maximum rack distribution, and comparison of similarly used datanodes.

## Important APIs, Types, and Functions
The configuration sets `DFS_NAMENODE_AVAILABLE_SPACE_RACK_FAULT_TOLERANT_BLOCK_PLACEMENT_POLICY_BALANCED_SPACE_PREFERENCE_FRACTION_KEY` to `0.6f` and installs `AvailableSpaceRackFaultTolerantBlockPlacementPolicy`. `setupCluster` builds four racks with five datanodes each. `testMaxRackAllocation` checks that a three-replica placement uses three distinct racks.

## Control Flow and State
The setup mirrors the non-rack-fault-tolerant available-space test: a local NameNode is formatted and started, all synthetic datanodes are added to topology, and capacity alternates between 100-percent and 50-percent remaining. `testChooseTarget` runs 10,000 target selections and expects the high-remaining selections to land between 52 and 55 percent. `testChooseDataNode` excludes all known nodes and fails only on NPE. `testChooseSimilarDataNode` creates three custom nodes and verifies tolerance comparison results.

## Dependencies and Integration Points
The tests integrate rack topology, block placement policy configuration, `DFSTestUtil`, `BlockManagerTestUtil.getStorageReportsForDatanode`, and default storage policy. The policy is accessed both through the `BlockPlacementPolicy` interface and via its concrete `chooseDataNode` and `compareDataNode` methods.

## Risks and Test Signals
The statistical target-selection assertion is sensitive to random distribution and policy probability changes. The rack allocation test provides a direct signal that the rack-fault-tolerant policy spreads replicas across racks, while null-handling catches failures in all-excluded candidate paths.

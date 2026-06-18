
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceBlockPlacementPolicy.java

## Purpose
`TestAvailableSpaceBlockPlacementPolicy` validates the available-space-aware replicated block placement policy. It checks that the policy can be installed by configuration, favors nodes with more remaining space at the expected probability, handles fully excluded candidate sets, and compares datanodes using tolerance rules.

## Important APIs, Types, and Functions
The setup uses four racks, five nodes per rack, three replicas, and 10,000 placement trials. It sets `DFS_NAMENODE_AVAILABLE_SPACE_BLOCK_PLACEMENT_POLICY_BALANCED_SPACE_PREFERENCE_FRACTION_KEY` to `0.6f`, tolerance limit to `93`, and policy class to `AvailableSpaceBlockPlacementPolicy`. Helpers update `DatanodeStorageInfo` utilization and synthetic heartbeats. Tests exercise `chooseTarget`, `chooseDataNode`, and `compareDataNode`.

## Control Flow and State
`setupCluster` creates 20 datanodes spread across racks, starts a local NameNode, installs all nodes into topology, and alternates 100-percent and 50-percent remaining capacity. `testChooseTarget` repeatedly chooses three targets and computes the fraction of selected nodes whose remaining percent is above 60, expecting about 52-55 percent. `testChooseDataNode` excludes all nodes to verify no NPE. `testChooseSimilarDataNode` and `testCompareDataNode` create ad hoc datanode sets with precise used-percent values to verify tolerance equality and ordering.

## Dependencies and Integration Points
This file touches the NameNode block manager, `NetworkTopology`, `DFSTestUtil`, storage reports from `BlockManagerTestUtil`, and storage policy selection. It integrates directly with the policy's comparison logic as well as the higher-level `chooseTarget` API.

## Risks and Test Signals
Statistical assertions can fail if random selection logic changes or if capacity percentages are calculated differently. The comparison tests provide deterministic signal for tolerance-limit behavior, while the replacement and excluded-node tests catch configuration and null-handling regressions.

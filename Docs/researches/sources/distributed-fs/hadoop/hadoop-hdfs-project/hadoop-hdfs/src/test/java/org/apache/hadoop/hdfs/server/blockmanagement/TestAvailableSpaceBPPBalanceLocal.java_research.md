
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceBPPBalanceLocal.java

## Purpose
This class tests `AvailableSpaceBlockPlacementPolicy` when local-node balancing is enabled. It verifies that a lightly used writer-local datanode is always selected for a single replica, while a heavily used writer-local datanode loses preference often enough to favor less-loaded nodes.

## Important APIs, Types, and Functions
Key configuration uses `DFS_NAMENODE_AVAILABLE_SPACE_BLOCK_PLACEMENT_POLICY_BALANCED_SPACE_PREFERENCE_FRACTION_KEY` set to `0.6f`, `DFS_NAMENODE_AVAILABLE_SPACE_BLOCK_PLACEMENT_POLICY_BALANCE_LOCAL_NODE_KEY` set to true, and `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` set to `AvailableSpaceBlockPlacementPolicy`. `setupCluster` creates two racks with three nodes each through `DFSTestUtil.createDatanodeStorageInfos`. `setupDataNodeCapacity` alternates 100 percent remaining and 25 percent remaining nodes.

## Control Flow and State
The static `@BeforeAll` setup formats and starts a NameNode, installs synthetic datanodes in network topology, and sets per-storage utilization through `updateHeartbeatWithUsage`. `testChooseLocalNode` loops 10,000 times with a zero-usage local node and expects that local node every time. `testChooseLocalNodeWithLocalNodeLoaded` loops 10,000 times with a 75-percent-used local node and asserts the non-local path wins more often than the local path.

## Dependencies and Integration Points
The tests integrate NameNode placement policy wiring, storage reports from `BlockManagerTestUtil`, rack topology, `TestBlockStoragePolicy.DEFAULT_STORAGE_POLICY`, and the policy's probabilistic selection algorithm.

## Risks and Test Signals
Because these are statistical tests, probability drift or random changes can create flakiness. The chosen thresholds are broad for the loaded-local-node case but exact for the unloaded-local-node case. Strong signal is that the balance-local feature does not erase locality when the writer is healthy and does not over-prefer locality when the writer is comparatively full.

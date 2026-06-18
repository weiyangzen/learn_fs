# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyWithNodeGroup.java

## Purpose
`TestReplicationPolicyWithNodeGroup` validates `BlockPlacementPolicyWithNodeGroup`, where placement must account for node-group fault domains below racks. It checks placement verification, write target selection, re-replication, deletion, boundary topologies, dependency exclusions, and favored-node behavior under node-group constraints.

## Important APIs, types, and functions
The class extends `BaseReplicationPolicyTest`, configures `NetworkTopologyWithNodeGroup`, and disables DFS network topology so tests run against node-group-aware topology. Helpers include `checkTargetsOnDifferentNodeGroup`, `isOnSameRack`, `isOnSameNodeGroup`, `chooseTarget`, `verifyNoTwoTargetsOnSameNodeGroup`, and `calculateRemaining`. It uses `BlockPlacementPolicyWithNodeGroup`, `BlockManager.newLocatedBlock`, `BlockPlacementStatus`, `NetworkTopology.getLastHalf`, `Host2NodesMap`, dependent host names, and storage policy deletion helpers inherited from the default policy.

## Control flow
`testVerifyBlockPlacement` creates located blocks with selected storages and checks placement status plus error descriptions for rack and node-group violations. `testChooseTarget1` through `testChooseTarget5` vary local writer health, exclusions, unavailable local rack, external writer, and no-space local storage. They assert that the first replica follows local preference when possible, later replicas spread across racks and node groups, and no two selected targets share a node group when avoidable. `testChooseTargetForLocalStorage` verifies fallback to another node on the writer's local rack when the writer has no space.

Re-replication tests pass existing chosen nodes and verify new targets complement rack and node-group placement. `testChooseReplicaToDelete` splits candidate replicas into rack/node-group priority sets and chooses deletions by node-group concentration and remaining space. Boundary topology tests replace the cluster topology with cases where one rack has a single node group or the requested replica count exceeds the number of node groups. Dependency testing adds dependent host relationships and verifies exclusions expand to all dependent nodes, reducing target count. Favored-node tests ensure usable favored nodes are selected, unusable favored nodes fall back within their node group, and remaining replicas still obey policy.

## State and persistence behavior
State includes the in-memory network topology, storage remaining space, excluded node sets, favored node lists, host dependency map, and replica candidate partitions. No persistent filesystem writes are required.

## Dependencies and integration points
The file tests the node-group specialization of the generic placement policy and its interaction with topology implementation, Host2NodesMap dependency awareness, storage policy deletion, and favored-node APIs. It depends heavily on the shared `BaseReplicationPolicyTest` harness.

## Risks and test signals
Signals are target lengths, exact storage identities in important cases, rack comparisons, node-group uniqueness, placement error text, deletion identity, and expanded exclusion-set size. The main risks are topology mutations shared across tests and assumptions about deterministic target choice where multiple nodes satisfy the same constraint. It protects against placing multiple replicas in the same node group, deleting replicas that reduce node-group diversity, and ignoring host dependency constraints.

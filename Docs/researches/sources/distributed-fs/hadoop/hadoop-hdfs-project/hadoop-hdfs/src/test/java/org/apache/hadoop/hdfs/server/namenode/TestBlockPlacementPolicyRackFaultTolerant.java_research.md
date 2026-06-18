# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBlockPlacementPolicyRackFaultTolerant.java

## Purpose

`TestBlockPlacementPolicyRackFaultTolerant` validates `BlockPlacementPolicyRackFaultTolerant` target selection across racks, including normal replication, additional datanode requests for existing blocks, and decommission scenarios where some racks have only one node.

## Important APIs, Types, and Functions

The setup configures `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` to `BlockPlacementPolicyRackFaultTolerant`, sets block/checksum sizes, starts 20 datanodes across 10 racks, and captures `NamenodeProtocols`, `FSNamesystem`, and `PermissionStatus`. Main helpers are `doTestChooseTargetNormalCase`, `doTestChooseTargetSpecialCase`, `shuffle`, `doTestLocatedBlock`, `doTestLocatedBlockRacks`, and `addToRacksCount`. The decommission test uses `DFSNetworkTopology`, `BlockManager`, `DatanodeManager`, datanode admin manager, erasure-coding policy setup, and `verifyBlockPlacement`.

## Control Flow

Normal choose-target testing creates multiple files with varying base replication and additional replication. It calls `namesystem.startFile`, `nameNodeRpc.addBlock`, and `nameNodeRpc.getAdditionalDatanode`, then verifies the located block contains the requested number of targets and rack counts differ by at most one. The special-case flow creates a 20-replica block, repeatedly shuffles partial existing locations, asks for additional datanodes, and checks the merged target set remains rack-balanced. The decommission flow starts a smaller DFS network topology, decommissions the client rack's only node, creates a striped-policy file, verifies target racks avoid the decommissioned rack and use four valid racks, then decommissions another single-rack node and verifies block-placement satisfaction.

## State and Persistence Behavior

State is in-memory MiniDFSCluster datanode topology, NameNode block target selection, datanode decommission state, and created file/block metadata. No restart or edit-log persistence is tested. The decommission path uses NameNode write locking around admin-manager state changes and waits for decommission completion before checking located blocks.

## Dependencies and Integration Points

The test integrates block placement policy configuration, NameNode file creation and add-block RPCs, additional-datanode selection, DFS network topology, datanode decommission management, erasure coding policy enablement, and striped block placement verification. Static rack mapping is reset before setup to avoid prior tests influencing topology.

## Risks and Edge Cases

Rack balance is asserted by count difference rather than exact target identity, making the test robust to target ordering but sensitive to topology assumptions. The special-case shuffle specifically protects against repeatedly choosing racks that already have more replicas when empty racks are available. Decommission timing can be asynchronous and relies on `GenericTestUtils.waitFor`. The decommission test reassigns `cluster` after shutting down the default fixture cluster, so teardown must tolerate that replacement.

## Test Signals

Signals include exact target counts for all replication/additional-replication cases, max rack-count minus min rack-count at most one, expected valid rack count of four under decommission, two replicas on `/RACK0` and `/RACK2` after additional placement, successful decommission completion, and `BlockPlacementStatus.isPlacementPolicySatisfied()` for located blocks after topology reduction.

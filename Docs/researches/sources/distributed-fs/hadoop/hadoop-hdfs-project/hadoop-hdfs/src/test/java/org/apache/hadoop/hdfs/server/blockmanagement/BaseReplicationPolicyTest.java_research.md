
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/BaseReplicationPolicyTest.java

## Purpose
`BaseReplicationPolicyTest` is an abstract fixture for block-placement-policy tests. It constructs a lightweight NameNode with a configurable `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY`, installs synthetic datanodes into the `NetworkTopology` and heartbeat manager, and exposes helper methods for subclasses to call `BlockPlacementPolicy.chooseTarget`.

## Important APIs, Types, and Functions
Important fields include `cluster`, `dataNodes`, `storages`, `namenode`, `dnManager`, `replicator`, and `striptedPolicy`. Subclasses implement `getDatanodeDescriptors(Configuration)`. `setupCluster` formats and starts a local NameNode using `DFSTestUtil.formatNameNode`, wires the selected placement policy, populates `NetworkTopology`, and initializes heartbeat stats. `updateHeartbeatWithUsage` writes storage utilization through `DatanodeStorageInfo.setUtilizationForTesting` and updates `HeartbeatManager`. Several overloaded `chooseTarget` helpers normalize writer, chosen-node, and excluded-node inputs.

## Control Flow and State
The setup path creates a fresh `HdfsConfiguration`, sets local NameNode URI and dirs, selects the policy class from `blockPlacementPolicy`, enables stale-node avoidance, then adds every synthetic datanode to both topology and heartbeat tracking. The fixture gives each datanode enough remaining capacity for writes by default. `tearDown` stops the NameNode after each test.

## Dependencies and Integration Points
The class depends on the NameNode/block manager stack, `DFSTestUtil`, `TestBlockStoragePolicy.DEFAULT_STORAGE_POLICY`, `PathUtils`, and `GenericTestUtils` log configuration. It exposes both replicated and striped placement policy handles, so subclasses can test policy variants without repeating cluster bootstrap.

## Risks and Test Signals
Risks include fixture state leaking through the NameNode or static temp dirs, spelling drift around `striptedPolicy`, and synthetic datanodes missing heartbeat/topology registration. Test signal is indirect: subclasses rely on this fixture to make placement decisions realistic enough to include capacity, rack, stale-node, and storage-policy inputs.

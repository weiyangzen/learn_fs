# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithNodeGroup.java

## Purpose
`TestBalancerWithNodeGroup` verifies that the balancer respects node-group-aware topology and block placement. It tests rack locality, node-group locality, no-move convergence when placement prevents movement, and configuration validation for `BlockPlacementPolicyWithNodeGroup`.

## Important APIs, Types, and Functions
The file uses `MiniDFSClusterWithNodeGroup`, `NetworkTopologyWithNodeGroup`, `BlockPlacementPolicyWithNodeGroup`, `BlockPlacementPolicy`, `BlockPlacementStatus`, `Balancer.run`, `ExitStatus`, and `LambdaTestUtils.intercept`. Helpers include `createConf`, `waitForHeartBeat`, `waitForBalancer`, `runBalancer`, `runBalancerCanFinish`, `getBlocksOnRack`, `verifyNetworkTopology`, and `verifyProperBlockPlacement`.

## Control Flow
`createConf` starts from `TestBalancer.initConf`, disables DFS network topology auto-use, sets the network topology implementation to node-group topology, and selects the node-group placement policy. Rack-locality and node-group tests build clusters with explicit racks and node groups, write a file to selected utilization, add a DataNode in a target rack/node group, run the balancer, and verify block placement after movement. The no-move test creates a topology where replicas cannot legally move without violating node-group policy and expects `NO_MOVE_PROGRESS`. `testBPPNodeGroup` intentionally enables DFS network topology while configuring node-group placement and expects cluster construction to fail.

## State and Persistence Behavior
State includes static node-group assignments on `MiniDFSClusterWithNodeGroup`, MiniDFSCluster block placement metadata, datanode reports, and network topology objects. Each test shuts down the cluster in `finally`.

## Dependencies and Integration Points
Integration points are HDFS topology resolution, node-group placement policy, balancer candidate selection, NameNode block placement verification, and shared `TestBalancer` utilities for file creation and summed capacities.

## Risks and Test Signals
Risks include static node-group configuration leakage, timing in heartbeat/balance polling, and exact exception-message dependency. Signals include topology instance checks, rack block-set preservation, `SUCCESS` or `NO_MOVE_PROGRESS` exit statuses, and per-block `BlockPlacementStatus.isPlacementPolicySatisfied`.

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestNetworkTopologyWithNodeGroup.java

## Purpose
Tests `NetworkTopologyWithNodeGroup`, adding node-group awareness below rack level for distance, sorting, random selection, and topology validation.

## Important APIs, Types, And Functions
Uses static `NetworkTopologyWithNodeGroup cluster`, `NodeBase` test nodes, `add()`, `getNumOfLeaves()`, `getNumOfRacks()`, `isOnSameRack()`, `isOnSameNodeGroup()`, `getDistance()`, `sortByDistance()`, `chooseRandom()`, and `getNodeGroup()`.

## Control Flow
Static initializer populates the cluster with eight nodes under `/domain/rack/nodegroup`. Tests check rack/nodegroup relationships, distance values, sorted ordering relative to local or compute nodes, random exclusion of a node path, root result for empty nodegroup, null location exception, and invalid rack-only topology rejection.

## State And Persistence Behavior
The cluster and data nodes are static and shared across all tests. Invalid add attempts are expected to fail without corrupting existing topology.

## Dependencies And Integration Points
Exercises Hadoop network topology extensions used by placement policies that distinguish rack and node group.

## Risks
Static topology state can make tests order-sensitive if a mutation unexpectedly succeeds. Random selection test assumes 100 picks cover all non-excluded nodes. Invalid topology validation must reject `/r2` rack-only nodes for node-group topology.

## Test Signals
Signals include eight leaves, three racks, same-rack and same-nodegroup booleans, distances 0/2/4/6/8, local/local-nodegroup/local-rack sort ordering, excluded node never chosen, and `IllegalArgumentException` containing `illegal network location`.

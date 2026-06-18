# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHost2NodesMap.java

## Purpose
`TestHost2NodesMap` verifies host-to-datanode mapping behavior when multiple datanodes share a host address, nodes are removed, and null or absent nodes are queried.

## Important APIs, Types, and Functions
The test uses `Host2NodesMap`, `DatanodeDescriptor`, and `DFSTestUtil.getDatanodeDescriptor`. The methods under test are `add`, `contains`, `getDatanodeByHost`, and `remove`.

## Control Flow
Setup creates four descriptors across three IPs, with two descriptors sharing `3.3.3.3` but different transfer ports, adds them to the map, and also calls `add(null)`. `testContains` checks that all inserted nodes are present while null and a non-inserted descriptor are absent. `testGetDatanodeByHost` checks single-host lookups and allows either descriptor for the shared host. `testRemove` removes absent, present, shared-host, null, and already-removed nodes while checking remaining lookup behavior.

## State and Persistence Behavior
State is an in-memory host-to-node map, including a multi-entry bucket for shared hosts. There is no persistent or cluster state.

## Dependencies and Integration Points
This unit test protects `DatanodeManager` host lookup behavior used during registration, report generation, and locality sorting.

## Risks and Edge Cases
Edge cases include null additions/removals, repeated host addresses, removing one node while another remains on the same host, and removing the last node for a host.

## Test Signals
Assertions verify boolean contains/remove results, exact descriptor returns for unique hosts, nullable returns for absent hosts, and either shared descriptor when both are present.

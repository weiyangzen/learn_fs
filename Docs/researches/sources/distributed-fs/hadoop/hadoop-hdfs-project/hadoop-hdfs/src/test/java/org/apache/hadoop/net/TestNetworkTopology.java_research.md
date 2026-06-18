# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/net/TestNetworkTopology.java

## Purpose
`TestNetworkTopology` validates Hadoop network topology tree behavior used by HDFS block placement: add/remove, rack counts, distance/weight calculations, sort-by-distance ordering, random node selection with include/exclude scopes, invalid topology handling, non-empty rack counts, and shuffle behavior.

## Important APIs, types, and functions
- `setupDatanodes()` creates twenty `DatanodeDescriptor` instances across data-center/rack paths, adds them to a static `NetworkTopology`, and marks two as decommissioned.
- Tests call `NetworkTopology.contains`, `getNumOfLeaves`, `add`, `remove`, `getNumOfRacks`, `isOnSameRack`, `getWeight`, `getWeightUsingNetworkLocation`, `getDistance`, `getDistanceByPath`, `sortByDistance`, `sortByDistanceUsingNetworkLocation`, `chooseRandom`, `countNumOfAvailableNodes`, `decommissionNode`, `recommissionNode`, and `shuffle`.
- `pickNodesAtRandom` repeatedly calls `chooseRandom` and returns frequency counts; `verifyResults` checks include/exclude outcomes.

## Control flow
Most tests use the shared topology populated in `@BeforeEach`. They assert simple containment/rack/distance behavior, then more complex sort ordering with deterministic seeds and randomization checks. Random-selection tests sample 100-200 choices and assert excluded nodes/racks are never selected while eligible nodes are selected at least once. `testInvalidNetworkTopologiesNotCachedInHdfs` starts a MiniDFSCluster with mismatched rack depths, waits for only one DataNode to register, updates `StaticMapping`, restarts the invalid node, and waits for both nodes to register with matching locations.

## State and persistence behavior
The topology object is static and persists across test methods; setup repeatedly adds the same logical nodes, relying on `NetworkTopology.add` idempotence by node identity/path. `testRemove` removes all nodes and re-adds them before exit. `testInvalidNetworkTopologiesNotCachedInHdfs` mutates static rack mapping and starts a real cluster, then shuts it down.

## Dependencies and integration points
The class integrates `DFSTestUtil` datanode descriptors, HDFS `MiniDFSCluster`, `NamenodeProtocols`, `DatanodeReportType`, `StaticMapping`, `NodeBase`, `DatanodeDescriptor` decommission state, and NetworkTopology logging/random support.

## Risks and edge cases
Sampling-based tests could be flaky if random selection changes or the sample count is insufficient. Static topology state can leak if add/remove semantics or failed tests leave it inconsistent. The invalid-topology cluster test uses sleeps and polling up to 180 seconds and is sensitive to DataNode registration timing.

## Test signals
Passing provides strong evidence that topology paths are validated, distance/weight values match rack depth, reader-local and rack-local sorting is stable with randomized ties, include/exclude scopes work, decommissioned/empty-rack accounting behaves, and invalid HDFS rack topology is not permanently cached after mapping repair.

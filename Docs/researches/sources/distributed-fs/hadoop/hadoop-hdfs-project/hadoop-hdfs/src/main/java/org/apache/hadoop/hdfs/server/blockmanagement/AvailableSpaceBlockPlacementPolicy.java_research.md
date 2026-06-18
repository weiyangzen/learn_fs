# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/AvailableSpaceBlockPlacementPolicy.java

## Purpose

`AvailableSpaceBlockPlacementPolicy` extends the default HDFS block placement policy by biasing random DataNode choices toward nodes with lower DFS-used percentage. It preserves default placement structure while improving space balance during writes and optional local-vs-local-rack selection.

## Important APIs, Types, and Functions

`initialize()` reads balanced-space preference fraction, tolerance, tolerance limit, and local-node balancing configuration. `chooseDataNode(scope, excludedNode, StorageType)` uses `DFSNetworkTopology.chooseRandomWithStorageTypeTwoTrial()` twice, while `chooseDataNode(scope, excludedNode)` uses `clusterMap.chooseRandom()` twice. `select()` compares the two candidates and applies a random preference percentage. `compareDataNode()` implements the utilization comparison. `chooseLocalStorage()` optionally compares the local node and local rack choice when `optimizeLocal` is enabled. `swapStorageTypes()` restores storage-type request counts after trying alternate paths.

## Control Flow

After default policy initialization, configuration values are validated with warnings and defaults for invalid tolerance ranges. On each DataNode choice, the policy samples two candidates, compares their used percentage, treats them equal when they are the same node, within tolerance, under the tolerance limit condition, or a sufficiently empty local node is being considered, and then either returns the first candidate or chooses the less-used candidate with configured probability.

For optimized local placement, the policy first tries local storage with cloned storage-type demands. It then optionally tries local rack with another clone, removes tentative results while comparing, and restores the storage-type map matching the selected path.

## State and Persistence Behavior

The policy stores only in-memory configuration-derived fields: `balancedPreference`, `balancedSpaceTolerance`, `balancedSpaceToleranceLimit`, and `optimizeLocal`. It does not persist state. Placement results affect NameNode block placement decisions that later become file/block metadata.

## Dependencies and Integration Points

It depends on `BlockPlacementPolicyDefault`, `DFSNetworkTopology`, `DatanodeDescriptor.getDfsUsedPercent()`, storage-type-aware random selection, and HDFS DFSConfigKeys. It is selected through NameNode block placement policy configuration and participates in normal write pipeline target selection.

## Risks and Edge Cases

Preference fractions outside `[0.0, 1.0]` are warned but still converted to an integer percentage, so values above 1.0 can make the preferred less-used candidate effectively always selected and negative values can invert behavior. The storage-type overload requires `clusterMap` to be a `DFSNetworkTopology`. The local optimization temporarily mutates `results`, `excludedNodes`, and storage-type maps and must keep those side effects balanced. Random tie behavior always returns `a` on exact equality.

## Test Signals

Tests should cover initialization validation, preference values at 0.5/1.0/out-of-range, tolerance and tolerance-limit comparisons, storage-type two-trial selection requiring `DFSNetworkTopology`, local optimization selecting local versus rack, restoration of `results`, `excludedNodes`, and storage-type counts, and fallback when one candidate is null.

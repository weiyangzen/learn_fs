# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicies.java

## Purpose
`BlockPlacementPolicies` is a small holder that creates and routes between the configured placement policy for replicated contiguous blocks and the configured placement policy for striped erasure-coded block groups.

## Important APIs, Types, and Functions
The constructor reads `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` and `DFS_BLOCK_PLACEMENT_EC_CLASSNAME_KEY`, instantiates both classes with `ReflectionUtils.newInstance`, and initializes each policy with `Configuration`, `FSClusterStats`, `NetworkTopology`, and `Host2NodesMap`. `getPolicy(BlockType)` returns the replicated policy for `CONTIGUOUS`, the EC policy for `STRIPED`, and throws `IllegalArgumentException` for unsupported block types.

## Control Flow
Construction eagerly creates and initializes both policy instances. Runtime selection is a switch on `BlockType`. `BlockManager` calls this holder for new block placement, reconstruction target selection, placement verification, replica deletion choices, slow-node exclusion toggles, and min-blocks-for-write settings.

## State and Persistence Behavior
The class stores two final policy instances. It has no persistence. Refresh behavior is handled by `BlockManager.refreshBlockPlacementPolicy()`, which replaces the entire holder with a newly constructed one.

## Dependencies and Integration Points
Dependencies are Hadoop configuration, `DFSConfigKeys`, `BlockType`, `NetworkTopology`, `FSClusterStats`, `Host2NodesMap`, `ReflectionUtils`, and the `BlockPlacementPolicy` base type. It is the bridge between block management logic and configurable rack/storage/EC placement implementations.

## Risks
Misconfigured policy class names fail at construction or initialization time. Both policies must implement all methods expected by `BlockManager`, including target choice, placement verification, replica deletion, slow-node exclusion, and minimum write targets. Adding a new `BlockType` requires updating this switch or callers will receive an `IllegalArgumentException`.

## Test Signals
Tests should verify default policy instantiation, custom replicated and EC policy class loading, initialization arguments, routing by `CONTIGUOUS` and `STRIPED`, replacement through `BlockManager.refreshBlockPlacementPolicy()`, and unsupported block type failure behavior.

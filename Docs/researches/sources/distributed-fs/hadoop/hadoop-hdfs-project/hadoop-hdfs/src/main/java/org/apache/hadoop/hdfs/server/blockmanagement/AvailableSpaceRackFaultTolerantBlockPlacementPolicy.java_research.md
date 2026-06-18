# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/AvailableSpaceRackFaultTolerantBlockPlacementPolicy.java

## Purpose

`AvailableSpaceRackFaultTolerantBlockPlacementPolicy` combines rack-fault-tolerant placement with an available-space bias. It keeps the rack-diversity behavior of `BlockPlacementPolicyRackFaultTolerant` while choosing between random candidates based on DataNode utilization.

## Important APIs, Types, and Functions

`initialize()` reads rack-fault-tolerant balanced-space preference and tolerance keys. `chooseDataNode(scope, excludedNode, StorageType)` samples two storage-type-compatible candidates from `DFSNetworkTopology`. `chooseDataNode(scope, excludedNode)` samples two regular candidates from `clusterMap`. `select()` applies `compareDataNode()` and the configured random preference. `compareDataNode()` treats candidates within tolerance as equal and otherwise orders by lower `getDfsUsedPercent()`.

## Control Flow

The policy initializes its superclass first, then validates preference/tolerance settings with warnings and default fallback for invalid tolerance. Each choice samples two candidates from the requested scope, compares them, and returns the less-used node with configured probability. If one sample is null, it returns the non-null sample.

## State and Persistence Behavior

State is limited to in-memory `balancedPreference` and `balancedSpaceTolerance` values. The class itself persists nothing; selected targets are persisted indirectly as NameNode block placement metadata after writes proceed.

## Dependencies and Integration Points

It depends on `BlockPlacementPolicyRackFaultTolerant`, `DFSNetworkTopology`, `NetworkTopology`, `DatanodeDescriptor`, `StorageType`, and rack-fault-tolerant DFS configuration keys. It is used when the NameNode is configured for rack-fault-tolerant available-space placement.

## Risks and Edge Cases

Like the non-rack policy, preference fractions outside the documented range are warned but still applied numerically. The storage-type path requires `DFSNetworkTopology`. There is no tolerance-limit or local-node optimization variant here, so behavior differs from `AvailableSpaceBlockPlacementPolicy`. Equal candidates return the first sample, which can preserve random-sampling bias.

## Test Signals

Tests should cover config initialization, invalid tolerance fallback, warnings for preference outside expected bounds, less-used candidate preference probability, equal-within-tolerance behavior, null candidate handling, storage-type selection through `DFSNetworkTopology`, and preservation of rack-fault-tolerant superclass behavior.

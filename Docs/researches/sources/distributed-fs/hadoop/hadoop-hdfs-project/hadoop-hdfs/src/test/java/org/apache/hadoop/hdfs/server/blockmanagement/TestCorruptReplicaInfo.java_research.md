# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCorruptReplicaInfo.java

## Purpose
`TestCorruptReplicaInfo` validates `CorruptReplicasMap` accounting and pagination for corrupt contiguous replicas and corrupt erasure-coded block groups. It ensures total, replicated, and striped corrupt counts are maintained independently and that test block-id listing APIs return the expected ranges.

## Important APIs, Types, and Functions
The test uses `CorruptReplicasMap`, `BlockIdManager`, `BlockType`, `BlockInfoContiguous`, `BlockInfoStriped`, `StripedFileTestUtil`, `DatanodeDescriptor`, and `CorruptReplicasMap.Reason`. Helpers are `getReplica`, `getStripedBlock`, `verifyCorruptBlocksCount`, and `addToCorruptReplicasMap`.

## Control Flow
The test starts with an empty map and checks invalid and zero-length listing requests. It creates arrays of 140 contiguous block IDs and 140 striped block IDs. It adds corrupt entries for two datanodes, verifying that multiple corrupt replicas of the same block do not increase the corrupt-block count. It removes entries and checks counts return to zero, then bulk-adds all contiguous and striped blocks and validates first-page and offset-page results.

## State and Persistence Behavior
All state is in memory. The file uses local maps to preserve stable `BlockInfo` instances by ID, mirroring how the production corrupt map keys by block identity.

## Dependencies and Integration Points
This is a focused unit test of corrupt replica metadata. It mocks `BlockIdManager` for legacy/striped classification and uses real block-info implementations for contiguous and striped blocks.

## Risks and Edge Cases
Risks include double-counting a block with corrupt reports from multiple datanodes, mixing contiguous and striped counters, bad pagination with the `startingBlockId` argument, and accepting invalid `n` values.

## Test Signals
Signals include exact size/counter assertions after each add/remove, null returns for invalid limits, empty arrays for zero limit, and array equality for contiguous and striped block ID slices.

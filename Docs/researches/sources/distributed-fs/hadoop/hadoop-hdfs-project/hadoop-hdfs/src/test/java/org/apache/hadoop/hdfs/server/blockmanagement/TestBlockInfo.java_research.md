
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockInfo.java

## Purpose
`TestBlockInfo` validates contiguous `BlockInfo` behavior used by `BlocksMap` and datanode storage block lists. It focuses on deletion state, storage addition and replacement, provided-storage detection, argument validation, and `DatanodeStorageInfo` block-list reordering.

## Important APIs, Types, and Functions
The tests use `BlockInfoContiguous`, `BlockCollection`, `DatanodeStorageInfo`, `DatanodeStorage`, `StorageType`, `GenerationStamp`, and `DatanodeStorageInfo.AddBlockResult`. Mockito supplies mock storages and datanode descriptors for storage-type scenarios. `testBlockListMoveToHead` exercises `DatanodeStorageInfo.moveBlockToHead`, `getBlockListHeadForTesting`, `findStorageInfo`, and `getNext`.

## Control Flow and State
`testIsDeleted` toggles `blockCollectionId` from a valid id to `INVALID_INODE_ID`. `testAddStorage` and provided-storage tests verify storage slots and `isProvided`. `testReplaceStorage` adds ten blocks to one storage, then adds one block to another storage on the same datanode and expects replacement semantics rather than an `ADDED` result. `testAddStorageWithDifferentBlock` expects `IllegalArgumentException` for mismatched block IDs. The block-list test builds a ten-block linked list, moves every block to the head, validates order, then performs random head moves.

## Dependencies and Integration Points
This is a unit-style test with `DFSTestUtil` factories and direct block/storage APIs. It probes data structures consumed by block reports, storage maps, provided-storage support, and datanode descriptor iteration.

## Risks and Test Signals
Important risks are broken linked-list invariants, incorrect storage replacement, accepting mismatched block reports, and failing to mark provided-backed blocks. The strongest test signal is structural: iterator length, head identity, and next pointers must remain consistent after deterministic and random moves.

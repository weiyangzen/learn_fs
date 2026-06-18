# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfoContiguous.java

## Purpose

`BlockInfoContiguous` is the `BlockInfo` implementation for traditionally replicated HDFS blocks. It maps each replica storage to one triplet slot and grows capacity when replication increases.

## Important APIs, Types, and Functions

Constructors accept a replication size alone or a `Block` plus replication size. `addStorage()` validates the reported block ID matches this block, ensures one free triplet slot, and stores the `DatanodeStorageInfo`. `removeStorage()` removes a storage by swapping the last populated triplet into the removed slot. `numNodes()` counts populated slots by scanning from the end. `isProvided()` detects any `StorageType.PROVIDED` replica. `isStriped()`, `getBlockType()`, and `hasNoStorage()` identify the contiguous block shape.

## Control Flow

When a DataNode reports a replica, `addStorage()` calls `ensureCapacity(1)`, appends the storage at the first free slot, and clears list pointers. When a replica disappears, `removeStorage()` requires the block to have been removed from the storage's linked list first, then compacts the array by moving the last populated triplet to the removed index and clearing the old tail.

## State and Persistence Behavior

State is inherited from `BlockInfo`: block identity, generation stamp, block collection ID, replication, UC state, and triplet location array. The subclass persists no separate fields. Triplet capacity can exceed current replica count after replication changes.

## Dependencies and Integration Points

It depends on `BlockInfo`, `DatanodeStorageInfo`, `StorageType`, `BlockType.CONTIGUOUS`, and `BlockManager` callers that manage replica reports and storage lists. It is used for non-erasure-coded HDFS files and provided-storage blocks.

## Risks and Edge Cases

Duplicate storage is not explicitly rejected in `addStorage()`; callers are expected to avoid duplicate additions. `removeStorage()` compaction can change storage slot indexes, so external code must not cache contiguous indexes across mutations. Assertions enforce that linked-list pointers are clear before removal. `hasNoStorage()` only checks slot 0, which is valid because compaction keeps populated slots packed from the front.

## Test Signals

Tests should cover block ID validation on add, capacity expansion after replication increase, packed slot behavior after removal, `numNodes()` after add/remove, provided-storage detection, no-storage detection, contiguous block type reporting, and duplicate-add caller behavior.

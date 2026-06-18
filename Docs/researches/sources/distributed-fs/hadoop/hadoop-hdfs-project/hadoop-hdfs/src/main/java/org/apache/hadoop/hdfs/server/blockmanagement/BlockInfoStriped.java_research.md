# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfoStriped.java

## Purpose

`BlockInfoStriped` is the `BlockInfo` implementation for erasure-coded HDFS block groups. It tracks one group block plus per-internal-block storage locations and block indexes, including over-replicated internal blocks.

## Important APIs, Types, and Functions

The constructor accepts a group `Block` and `ErasureCodingPolicy`, sizes initial triplets to data plus parity units, initializes `indices` to -1, and stores the policy. Accessors expose total/data/parity counts, cell size, real data/total block counts for short final stripes, and the policy. Storage APIs include `addStorage()`, private `addStorage(storage,index,blockIndex)`, `removeStorage()`, `getStorageBlockIndex()`, `getBlockOnStorage()`, `numNodes()`, `hasNoStorage()`, and `isProvided()`. Capacity helpers `findSlot()`, `findStorageInfoFromEnd()`, and `ensureCapacity()` handle over-replication. `spaceConsumed()` computes EC storage consumption. `StorageAndBlockIndex` and `getStorageAndIndexInfos()` expose storage/index iteration.

## Control Flow

When a DataNode reports an internal block, `addStorage()` validates that the reported ID is striped and masks to this block-group ID. The low index bits choose the canonical slot for that internal block. If that slot is occupied by another storage, the code treats the report as over-replication: it returns true if the same storage is already recorded, otherwise it finds or creates an overflow slot. The selected slot stores the storage and its internal block index.

Removal searches from the end so overflow entries are removed before canonical entries when the same storage appears multiple times. It clears storage, list pointers, and the index byte without compacting, because canonical slot positions matter. Iteration skips null storage slots and returns storage plus block index pairs.

## State and Persistence Behavior

In addition to inherited `BlockInfo` state, this class stores immutable `ErasureCodingPolicy` and mutable `indices` aligned one-to-one with triplet slots. The group block length represents data length, while `spaceConsumed()` accounts for data plus parity. Persistent block-group identity and EC policy are NameNode metadata; the triplet/index location mapping is maintained in memory from block reports and namespace state.

## Dependencies and Integration Points

It depends on `BlockIdManager` striped ID helpers, `ErasureCodingPolicy`, `StripedBlockUtil`, `BlockType.STRIPED`, `BlockUCState`, and `DatanodeStorageInfo`. It integrates with erasure-coded file writes, block reports, reconstruction, block group accounting, and balancer/mover code that maps group blocks to internal blocks.

## Risks and Edge Cases

Index alignment is critical: canonical slots map directly to internal block indexes, while overflow slots carry explicit index bytes. Removing storage leaves holes, so `numNodes()` counts non-null slots rather than relying on packed layout. `getRealDataBlockNum()` uses `(getNumBytes() - 1) / cellSize + 1`; zero-length groups would need careful handling by callers. Provided storage is explicitly unsupported for striped blocks. Capacity growth copies both triplets and indices; any mismatch corrupts reported internal block mapping.

## Test Signals

Tests should cover canonical add, over-replicated add to overflow slots, duplicate storage add idempotence, removal from overflow and canonical slots, storage block index lookup, `getBlockOnStorage()` ID construction, short final stripe real data counts, space consumed calculation, iterator skipping holes, capacity expansion preserving indices, and rejection of non-striped or wrong-group reported blocks.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfo.java

## Purpose

`BlockInfo` is the abstract NameNode metadata record for a block or erasure-coded block group. It extends protocol `Block` with owning block collection ID, replica/storage locations, per-storage linked-list pointers, replication information, and under-construction state.

## Important APIs, Types, and Functions

Core state accessors include `getReplication()`, `setReplication()`, `getBlockCollectionId()`, `setBlockCollectionId()`, `delete()`, `isDeleted()`, `getStorageInfos()`, `getDatanode()`, `getCapacity()`, and abstract storage APIs `numNodes()`, `addStorage()`, `removeStorage()`, `hasNoStorage()`, `isProvided()`, `isStriped()`, and `getBlockType()`.

Location internals are stored in `triplets`: for each storage slot, `[DatanodeStorageInfo, previous BlockInfo, next BlockInfo]`. Helper methods read and mutate storage, previous, and next slots; `findStorageInfo()` resolves by DataNode or storage; `listInsert()`, `listRemove()`, and `moveBlockToHead()` maintain DataNode storage block lists. Under-construction APIs include `getUnderConstructionFeature()`, `getBlockUCState()`, `isComplete()`, `isUnderRecovery()`, `isCompleteOrCommitted()`, `convertToBlockUnderConstruction()`, `convertToCompleteBlock()`, `setGenerationStampAndVerifyReplicas()`, and `commitBlock()`.

## Control Flow

Concrete subclasses allocate triplet capacity and implement how reported blocks map to storage slots. Block-map and block-report paths call `addStorage()` and insert the block into each `DatanodeStorageInfo` list. Removal requires the block to be detached from the list first, enforced by assertions. List operations update previous/next pointers in-place to avoid per-replica linked-list entry objects.

For writes and recovery, complete blocks can be converted to under-construction with expected storage targets. Repeated conversion updates the existing `BlockUnderConstructionFeature`. Commit validates block ID consistency, moves the UC state to committed, updates length, sets the final generation stamp, and returns stale replicas that should be invalidated or handled by recovery logic.

## State and Persistence Behavior

`BlockInfo` carries persistent NameNode metadata: block ID, length, generation stamp inherited from `Block`, owning block collection ID, replication for contiguous blocks, and under-construction metadata. The in-memory `triplets` and linked-list pointers are reconstructed from block reports/fsimage and are optimized for memory. `bcId` is volatile because block collection ownership can be read concurrently.

## Dependencies and Integration Points

It depends on `Block`, `BlockCollection`, `BlocksMap`, `DatanodeStorageInfo`, `DatanodeDescriptor`, `StorageType.PROVIDED`, `BlockUnderConstructionFeature`, `ReplicaUnderConstruction`, `BlockUCState`, and `LightWeightGSet.LinkedElement`. It is central to `BlockManager`, storage reports, file inode block arrays, replication, reconstruction, deletion, and lease recovery.

## Risks and Edge Cases

The triplet array is compact but assertion-heavy; corruption of slot alignment breaks block-list traversal. `getStorageInfos()` exposes an iterator tied to `BlocksMap.StorageIterator`. Provided storage matching uses storage ID rather than DataNode object and may return a provided storage after scanning local matches. `moveBlockToHead()` assumes non-null previous when moving a non-head block. Many consistency checks are Java assertions, so production builds may not catch misuse. `commitBlock()` throws on block ID mismatch but assumes UC state exists.

## Test Signals

Tests should cover triplet capacity, storage add/remove in contiguous and striped subclasses, DataNode and provided-storage lookup, linked-list insert/remove/head movement, deletion via invalid block collection ID, equality/hash behavior inherited from `Block`, UC conversion/update, commit length and generation stamp changes, stale replica detection, and malformed list assertions in assertion-enabled tests.

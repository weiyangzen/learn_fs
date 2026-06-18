# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlocksMap.java

## Purpose

`BlocksMap` is the NameNode's block-to-metadata index. It maps block IDs to `BlockInfo`, tracks which block collection owns a block, and links block metadata to datanode storage locations.

## Important APIs and types

- `addBlockCollection` inserts or reuses a `BlockInfo` and sets its block collection ID.
- `removeBlock` removes a block from the map and all datanode storage lists.
- `getStoredBlock`, `getStorages`, `numNodes`, `removeNode`, `size`, `getBlocks`, and `getCapacity` expose lookup and iteration.
- `StorageIterator` iterates non-null storages from a `BlockInfo`, including striped blocks with sparse slots.
- `getReplicatedBlocks` and `getECBlockGroups` expose block-type counters.

## Control flow

The map is backed by a `LightWeightGSet` sized by constructor capacity. Its iterator disables modification tracking because the map is expected to be accessed under the FSNamesystem lock. Adding a block increments replicated or striped counters only when the block is newly inserted. Removing a block first removes it from the GSet, decrements counters, asserts it is no longer owned by an inode, then walks storage slots backwards removing the block from each datanode storage. Removing a node detaches that datanode's storage from the block and removes the block entirely if it is both deleted and has no storage.

## State and persistence behavior

`BlocksMap` is in-memory NameNode metadata. It can be cleared or closed, and counters are maintained with `LongAdder`. Persistent namespace state is stored elsewhere in fsimage/edit logs.

## Dependencies and integration points

It integrates `Block`, `BlockInfo`, `BlockCollection`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `INodeId`, `GSet`, and `LightWeightGSet`. It is central to block reports, replication, corruption handling, deletion, and cache management.

## Risks and edge cases

Iterator behavior intentionally tolerates concurrent modifications only because external locks are assumed; using it without locks can miss entries. Counter correctness depends on every insertion and removal path pairing increments/decrements. `removeBlock` asserts ownership is invalid before final removal, so callers must clear block collection ownership first.

## Test signals

Tests should cover add/reuse behavior, replicated versus striped counters, storage iteration with null striped slots, remove-node cleanup, block removal from datanode lists, clear/close behavior, and no-storage deleted block eviction.

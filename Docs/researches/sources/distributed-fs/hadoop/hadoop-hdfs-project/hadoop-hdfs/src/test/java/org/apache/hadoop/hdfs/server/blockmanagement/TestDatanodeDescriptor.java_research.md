# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeDescriptor.java

## Purpose
`TestDatanodeDescriptor` tests two core descriptor behaviors: limiting invalidation commands returned to a datanode and maintaining accurate block counts as blocks are added or removed from datanode storages.

## Important APIs, Types, and Functions
The test uses `DatanodeDescriptor`, `DatanodeStorageInfo`, `DatanodeStorageInfo.AddBlockResult`, `BlocksMap.removeBlock`, `BlockInfoContiguous`, `Block`, `GenerationStamp`, `DFSTestUtil`, and `BlockManagerTestUtil`.

## Control Flow
`testGetInvalidateBlocks` creates ten blocks, queues them for invalidation on one descriptor, then calls `getInvalidateBlocks` with a limit of eight. The first call returns eight blocks and the second returns the remaining two. `testBlocksCounter` creates a descriptor with storage info, adds one block, tries to remove a missing block, tries to add an existing block again, adds a second block, and removes both blocks while checking `numBlocks`.

## State and Persistence Behavior
State is in-memory descriptor metadata: invalidation queues, storage-to-block membership, and the descriptor block counter. There is no MiniDFSCluster.

## Dependencies and Integration Points
The block counter checks protect `BlocksMap` and `DatanodeStorageInfo` interactions. The invalidation limit behavior is consumed by heartbeat command generation.

## Risks and Edge Cases
Risks include returning too many invalidation blocks in one heartbeat, failing to drain remaining invalidations, double-counting duplicate block additions, or decrementing counts for non-existent removals.

## Test Signals
Assertions verify the exact invalidation batch lengths, `ADDED` return values only for first additions, non-`ADDED` for duplicate add, false removal of a missing block, true removals of present blocks, and exact `numBlocks` after every transition.

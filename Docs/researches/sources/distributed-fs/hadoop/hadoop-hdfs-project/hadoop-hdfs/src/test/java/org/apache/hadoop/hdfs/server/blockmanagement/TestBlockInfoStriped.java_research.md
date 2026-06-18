
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockInfoStriped.java

## Purpose
`TestBlockInfoStriped` validates erasure-coded `BlockInfoStriped` storage indexing, removal, serialization, block lookup, and input validation across all configured EC policies. It is parameterized over `StripedFileTestUtil.getECPolicies()`.

## Important APIs, Types, and Functions
The class uses `BlockInfoStriped`, `ErasureCodingPolicy`, `Block`, `DatanodeStorageInfo`, `MiniDFSCluster`, `DistributedFileSystem`, `DFSck`, and `Whitebox` inspection of the private `indices` array. `createReportedBlocks` generates internal block IDs by adding offsets to a negative base block-group ID. Tests exercise `addStorage`, `removeStorage`, `findStorageInfo`, `numNodes`, `getCapacity`, `write`, and validation of mismatched block types or block groups.

## Control Flow and State
`testAddStorage` adds even-indexed then odd-indexed storages, checks capacity and indices, re-adds the same reports, then adds duplicate internal blocks from additional storages to force capacity growth. `testRemoveStorage` removes selected storages, checks `-1` index markers, adds duplicate reports into freed and extended slots, then removes those duplicates. `testGetBlockInfo` builds a MiniDFSCluster, writes an EC file, removes one storage from the NameNode's stored block info, and runs `dfsck -blockId` to ensure output does not contain `null`. `testWrite` verifies serialized bytes match raw `Block` fields.

## Dependencies and Integration Points
The file integrates EC policy definitions, NameNode block manager storage lookup, `DFSck`, MiniDFSCluster EC setup, and `DFSTestUtil` block discovery. It touches both pure in-memory `BlockInfoStriped` behavior and an end-to-end NameNode/DFSck reporting path.

## Risks and Test Signals
Risks include stale `indices` entries after removal, duplicate internal block miscounting, null storage output in diagnostics, and accidental acceptance of contiguous or different-group blocks. Test signals are strong because they assert exact index arrays, capacity behavior, serialization bytes, and expected exceptions.

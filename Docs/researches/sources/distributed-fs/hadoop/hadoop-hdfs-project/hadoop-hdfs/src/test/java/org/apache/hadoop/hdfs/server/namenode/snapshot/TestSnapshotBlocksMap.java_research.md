# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotBlocksMap.java

## Purpose

`TestSnapshotBlocksMap` verifies that snapshot-protected files keep correct block-map ownership while current files are deleted, renamed, appended, checkpointed, or left with zero-size under-construction blocks. It is a NameNode block-management regression suite for snapshot interactions.

## Important APIs, types, and helpers

- Public APIs under test: `delete`, `createSnapshot`, `allowSnapshot`, `setReplication`, `append`, safe mode and namespace save operations.
- Internal APIs: `BlockManager.getStoredBlock`, `BlockInfo.getBlockCollectionId`, `INodeFile.getBlocks`, `FSDirectory.getINode`, and `NameNodeAdapter.saveNamespace`.
- Helpers: `assertBlockCollection(String, int, FSDirectory, BlockManager)` and `assertBlockCollection(BlockManager, INodeFile, BlockInfo)` ensure every block points to the expected owning inode.
- Constants: `INVALID_INODE_ID` marks blocks no longer owned by any inode.

## Control flow

The fixture creates a three-datanode cluster with a `1024` block size and captures `FSDirectory`, `BlockManager`, and the HDFS client.

`testDeletionWithSnapshots` first shows normal deletion invalidates block collection IDs. It then creates multiple snapshots under `sub1`, changes replication so an inode becomes snapshot-aware, deletes current files, deletes a snapshot, and checks that blocks remain owned while any snapshot still references the file. It also verifies a deleted snapshot path no longer resolves.

`testReadSnapshotFileWithCheckpoint` and `testReadRenamedSnapshotFileWithCheckpoint` reproduce HDFS-5427 style flows: create a snapshot, delete or rename/delete the current file, checkpoint, restart the NameNode from fsimage, and read the snapshot file.

The zero-size block tests construct under-construction files by appending and manually adding a new block through NameNode RPC. After snapshots, deletes, directory deletes, or rename-then-delete flows, the snapshot copy must retain only the completed block and drop the zero-size block. The final test starts from a zero-length file, appends data after a snapshot, deletes it, and verifies fsimage save succeeds.

## State and persistence behavior

The central state is the block map's relationship between `BlockInfo` and `INodeFile`. The tests explicitly check when block collection IDs should become `INVALID_INODE_ID` and when they must remain attached because a snapshot copy owns the block.

Persistence is covered by checkpoint/saveNamespace plus NameNode restart, followed by reading snapshot files or saving fsimage. This catches cases where snapshot files survive in memory but lose block ownership or serialize incorrectly.

## Dependencies and integration points

The file integrates client file operations, snapshots, NameNode RPC block allocation, block manager internals, `INodeFile` state, checkpointing, safe mode, and snapshot path resolution. It is also used indirectly by `TestSnapshotDeletion`, which calls `TestSnapshotBlocksMap.assertBlockCollection`.

## Risks and maintenance notes

- The tests inspect mutable internal block metadata directly, so block manager representation changes can require updates.
- Manual `addBlock` RPC use creates a precise under-construction state; changes to append/block-allocation protocols may affect setup.
- Timings around checkpoint and restart are bounded by JUnit timeouts but still depend on cluster lifecycle stability.
- The zero-size block cases protect against subtle fsimage corruption and block leak regressions.

## Test signals

Key signals are block count per `INodeFile`, stored-block object identity, block collection IDs, snapshot path readability after checkpoint/restart, absence of deleted snapshot inodes, removal of zero-size trailing blocks from snapshot copies, and successful namespace save after deleting an appended file whose snapshot was zero-length.

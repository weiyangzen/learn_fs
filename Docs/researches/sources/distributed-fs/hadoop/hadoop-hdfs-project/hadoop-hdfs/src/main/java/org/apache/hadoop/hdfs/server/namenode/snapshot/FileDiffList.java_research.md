# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileDiffList.java

## Purpose

`FileDiffList` is the file-specific `AbstractINodeDiffList` implementation. It creates `FileDiff` objects, stores snapshot file attribute copies, preserves block snapshots for truncate, and determines which blocks can be reclaimed when a file snapshot diff is removed.

## Important APIs, Types, And Functions

Key methods are `createDiff`, `createSnapshotCopy`, `destroyAndCollectSnapshotBlocks`, `saveSelf2Snapshot`, `findEarlierSnapshotBlocks`, `findLaterSnapshotBlocks`, and `combineAndCollectSnapshotBlocks`. It uses `BlockInfo` arrays to compare removed, earlier, later, and current file block references.

## Control Flow

When a file records itself to a snapshot, `saveSelf2Snapshot` creates or updates the latest diff and optionally stores the current block list. Snapshot deletion calls `combineAndCollectSnapshotBlocks`: if the removed diff has blocks, it may copy them to the prior diff, find later/current block arrays, skip blocks still referenced by either side, protect a truncate-recovery block, and collect remaining blocks for deletion. If the removed diff has no block array and the current file is deleted, it clears the file via `FileWithSnapshotFeature`.

## State And Persistence Behavior

The list itself is persisted by snapshot image formats through its `FileDiff` entries. Block arrays inside diffs are in-memory references restored from protobuf image data. Deletion mutates neighboring diffs by copying block arrays backward when needed and emits block deletions through reclaim context.

## Dependencies And Integration Points

It depends on `AbstractINodeDiffList`, `INodeFile`, `INodeFileAttributes.SnapshotCopy`, block management classes, and `FileWithSnapshotFeature`. It is used by file mutation, truncate, snapshot delete, FSImage load/save, and quota/block collection paths.

## Risks And Edge Cases

The block comparison is reference-based for earlier/later arrays and must avoid deleting blocks still shared by snapshots or current files. Truncate recovery has a special `dontRemoveBlock` path. `findEarlierSnapshotBlocks` and `findLaterSnapshotBlocks` rely on correct binary-search insertion point handling. Current-file-deleted state changes the meaning of missing removed block arrays.

## Test Signals

Useful tests cover append/truncate across multiple snapshots, deleting earlier/middle/later snapshots, current deleted file cleanup, under-construction truncate recovery blocks, FSImage reload of block arrays, and quota deltas after block collection.

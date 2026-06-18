# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FileDiff.java

## Purpose

`FileDiff` records a file's state at a snapshot boundary. It captures the file length, optional file attribute snapshot copy, and, for truncate/block-list changes, a snapshot copy of block references needed to decide which blocks remain live.

## Important APIs, Types, And Functions

The class extends `AbstractINodeDiff<INodeFile, INodeFileAttributes, FileDiff>`. Important methods are `getFileSize`, `setBlocks`, `getBlocks`, `combinePosteriorAndCollectBlocks`, `write`, `destroyDiffAndCollectBlocks`, and `destroyAndCollectSnapshotBlocks`. `setBlocks` copies only enough `BlockInfo` entries to cover the saved file size.

## Control Flow

Normal creation records `file.computeFileSize()` and leaves blocks unset until a caller needs to preserve block references. FSImage load uses the constructor that accepts snapshot attributes and file size, then may call `setBlocks`. Snapshot deletion calls into `FileWithSnapshotFeature.updateQuotaAndCollectBlocks`, which combines block ownership with prior/later snapshots. Direct destruction emits blocks in the stored snapshot block list to `BlocksMapUpdateInfo`.

## State And Persistence Behavior

Durable fields are snapshot ID, file size, optional snapshot inode attributes, and, in protobuf FSImage, optional block references. The older non-protobuf `write` method writes snapshot ID, size, and attributes but not block arrays directly. After `destroyAndCollectSnapshotBlocks`, the block snapshot reference array is nulled to prevent duplicate collection.

## Dependencies And Integration Points

It depends on `BlockInfo`, `INodeFile`, file attribute snapshots, `FSImageSerialization`, and `FileWithSnapshotFeature`. It is held by `FileDiffList`, serialized by snapshot FSImage formats, and consumed during truncation, snapshot deletion, quota calculation, and block map cleanup.

## Risks And Edge Cases

`setBlocks` is intentionally one-shot; later calls do nothing, so callers must pass the correct block array the first time. The file-size loop assumes block lengths cover file length correctly. Block references are shared with block manager structures and must be collected only when no current, earlier, or later snapshot needs them. Snapshot attribute ACL references must be released by higher-level cleanup.

## Test Signals

Tests should cover truncation snapshots with partial block lists, repeated `setBlocks` calls, FSImage round trip of file diff blocks, snapshot deletion that preserves blocks referenced by earlier/later snapshots, and block collection when the last snapshot copy is removed.

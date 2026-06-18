# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotFSImageFormat.java

## Purpose

`SnapshotFSImageFormat` is the legacy binary FSImage helper for snapshot data. It saves and loads snapshot IDs, snapshot quota, file and directory diff lists, created/deleted child lists, and reference-node maps outside the protobuf image path.

## Important APIs, Types, And Functions

Top-level APIs include `saveSnapshots`, `saveDirectoryDiffList`, `saveFileDiffList`, `loadFileDiffList`, `loadCreated`, `loadSnapshotList`, and `loadDirectoryDiffList`. Internal helpers include `saveINodeDiffs`, `loadFileDiff`, `loadCreatedList`, `loadDeletedList`, `loadSnapshotINodeInDirectoryDiff`, and `loadDirectoryDiff`. Nested `ReferenceMap` serializes and reloads `INodeReference.WithCount` objects while avoiding duplicate referred subtree writes.

## Control Flow

Saving writes snapshots by name-order ID list plus quota, and writes diff lists in reverse order so created-list names can resolve against posterior diffs during load. File diff loading reads snapshot ID, file size, and optional file attributes, then prepends each diff while threading posterior references. Directory diff loading reads snapshot ID, child size, snapshot-root/copy data, created-list names resolved through `loadCreated`, deleted inode records, and builds a `DirectoryDiff` with the current first diff as posterior.

## State And Persistence Behavior

This class persists the same logical snapshot state as the protobuf format but through `DataInput`/`DataOutput`. Created lists store names only; deleted lists store full inode images. `ReferenceMap` persists referred inodes once and subsequent references by ID, and tracks directory IDs whose subtrees have already been processed.

## Dependencies And Integration Points

It depends on `FSImageFormat.Loader`, `FSImageSerialization`, inode and attribute classes, `DirectoryWithSnapshotFeature`, `FileDiffList`, `Snapshot`, `INodeReference`, and HDFS snapshot diff tooling. It is retained for older FSImage compatibility and upgrade paths.

## Risks And Edge Cases

Created-list resolution can fail if reverse diff order or current children are inconsistent, producing an `IOException`. Reference-map consistency is required for renamed nodes and shared subtrees. The older file diff writer does not write block arrays here, unlike protobuf snapshot diff handling, so compatibility expectations must remain clear. Snapshot root versus ordinary snapshot copy is encoded with booleans and must be read in the same order.

## Test Signals

Tests should cover legacy FSImage save/load for snapshots, created-list resolution through posterior deleted entries and current children, deleted inode block-map updates, reference reuse, snapshot quota restoration, and compatibility with directories/files containing ACLs, XAttrs, quotas, and references.

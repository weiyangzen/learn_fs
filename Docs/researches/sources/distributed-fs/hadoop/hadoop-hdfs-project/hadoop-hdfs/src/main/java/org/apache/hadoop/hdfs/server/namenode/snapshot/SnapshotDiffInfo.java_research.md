# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDiffInfo.java

## Purpose

`SnapshotDiffInfo` accumulates the full, non-paginated difference between two snapshots or a snapshot and current state. It records modified files/directories, directory child diffs, rename source/target pairs, traversal statistics, and generates a `SnapshotDiffReport`.

## Important APIs, Types, And Functions

The package-private class stores `snapshotRoot`, `snapshotDiffScopeDir`, `from`, `to`, a sorted `diffMap`, `dirDiffMap`, `renameMap`, and stats counters. `RenameEntry` stores source and target byte-array paths. Key methods are `addDirDiff`, `addFileDiff`, `setRenameTarget`, stats increment methods, `isFromEarlier`, and `generateReport`.

## Control Flow

`DirectorySnapshottableFeature` recursively calls `addDirDiff` and `addFileDiff`. Directory diffs add the directory to `diffMap`, store its `ChildrenDiff`, and detect renames by matching created references and deleted `INodeReference.WithName` entries with the same inode ID. `generateReport` walks `diffMap` in inode-path order, emits a MODIFY entry for every changed inode, then expands directory child diffs into CREATE, DELETE, or RENAME entries depending on direction and completed rename pairs.

## State And Persistence Behavior

The class is request-scoped and not persisted. It holds references to live/snapshot inode objects and byte-array relative paths while a diff RPC is computed. The generated `DiffStats` carries traversal counts and child-listing time into the response.

## Dependencies And Integration Points

It depends on HDFS protocol `SnapshotDiffReport`, inode classes, `ChildrenDiff`, `INodeReference`, Guava `SignedBytes`, and `ChunkedArrayList`. It is used by `SnapshotManager.diff` through `DirectorySnapshottableFeature.computeDiff`.

## Risks And Edge Cases

The recursive inode comparator compares parent chains and local names, so it assumes stable inode parent links during computation. Rename detection needs both source and target; incomplete pairs are reported as create/delete. Direction reversal flips create/delete and rename source/target. The report always includes MODIFY before child-level entries for changed directories. Large diffs can grow memory because this is the full-report path.

## Test Signals

Tests should cover create/delete/modify/rename reports in both directions, incomplete rename pairs, descendant-scoped paths, sorted output order, stats counters, current-state comparisons with null snapshots, and large reports using `ChunkedArrayList`.

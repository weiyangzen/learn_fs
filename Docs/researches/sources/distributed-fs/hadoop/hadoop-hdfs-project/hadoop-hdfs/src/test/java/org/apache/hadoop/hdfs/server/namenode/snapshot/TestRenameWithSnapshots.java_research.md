# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRenameWithSnapshots.java

## Purpose

`TestRenameWithSnapshots` is a slow JUnit 5 integration/regression suite for HDFS rename behavior when snapshots are present. It drives a `MiniDFSCluster` and asserts that rename, overwrite, delete-snapshot, append, quota, and restart/checkpoint paths preserve snapshot-visible namespace state, block ownership, `INodeReference` reference counts, snapshot diff ordering, and quota accounting.

The file is especially focused on HDFS snapshot internals rather than only public API results. Many tests inspect `FSDirectory`, `INodeDirectory`, `INodeFile`, `INodeReference.WithName`, `INodeReference.DstReference`, `INodeReference.WithCount`, `DirectoryDiff`, `FileDiff`, and `ChildrenDiff` directly after public operations.

## Important APIs, types, and helpers

- Public client APIs under test: `DistributedFileSystem.rename`, `rename(..., Rename.OVERWRITE)`, `createSnapshot`, `deleteSnapshot`, `allowSnapshot`, `disallowSnapshot`, `getSnapshotDiffReport`, `append`, `truncate`, `setReplication`, `setQuota`, `getContentSummary`, and `getQuotaUsage`.
- Internal state APIs: `FSNamesystem`, `FSDirectory`, `INodeDirectory.getDiffs`, `INodeFile.getDiffs`, `INodeReference.WithCount.getReferenceCount`, `INodeReference.WithCount.getLastWithName`, `QuotaCounts`, and `ReadOnlyList`.
- Snapshot helpers: `SnapshotTestHelper.createSnapshot`, `getSnapshotPath`, `dumpTree2File`, and `compareDumpedTreeInFile`.
- `assertSizes(int createdSize, int deletedSize, ChildrenDiff diff)` checks the created/deleted child lists in a directory diff.
- `existsInDiffReport` validates `SnapshotDiffReport.DiffReportEntry` values for `MODIFY`, `CREATE`, `DELETE`, and `RENAME`.
- `restartClusterAndCheckImage(boolean compareQuota)` persists the current namespace through edit-log replay and fsimage save/load, then compares dumped trees before restart, after edit replay, and after fsimage load.
- Mockito/Whitebox based tests replace `INodeDirectory` or `FSDirectory` behavior to force failure paths and verify rename undo logic.

## Control flow and scenario coverage

The fixture builds a three-datanode `MiniDFSCluster`, captures `FSNamesystem`, `FSDirectory`, and the cluster `DistributedFileSystem`, then tears the cluster down per test. Tests generally follow this pattern: create snapshottable directories and files, take snapshots, perform rename or related mutation, inspect public snapshot paths and internal inode/diff state, then often call `restartClusterAndCheckImage`.

Basic rename diff behavior is covered first. The suite distinguishes files created after a snapshot, files already present in a snapshot, multiple renames across snapshot intervals, file renames under child directories, directory renames, and combined directory/file rename reports. It expects the snapshot diff report to emit root or child `MODIFY` entries plus precise `CREATE` or `RENAME` entries.

Cross-snapshottable-directory movement is a central path. Tests move files and directories among `/dir1`, `/dir2`, and `/dir3`, with snapshots taken before, between, and after moves. These validate that a moved subtree records subsequent changes against the correct prior snapshot root, and that snapshot paths in the source directory remain readable even when the current inode has moved elsewhere.

Snapshot deletion after rename is heavily tested. Cases such as `testRenameDirAndDeleteSnapshot_1` through `_7`, `testRenameFileAndDeleteSnapshot`, and the two `testRenameMoreThanOnceAcrossSnapDirs` variants combine reference nodes and directory/file diffs while snapshots are deleted in different orders. Assertions check that deleted snapshot diffs are combined into the correct prior diff, not merely the nearest snapshot in the destination tree, and that newly-created post-rename children are destroyed when the only snapshot retaining them is deleted.

Undo/failure paths are deliberately forced. `testRenameUndo_1` through `_7` cover destination `addChild` failure, second rename failure, overwrite where the destination is itself a reference node, quota exceptions, failure while removing the overwritten destination, invalid reserved `.snapshot` target names, and quota verification gaps. These tests assert that after rollback the source tree, destination tree, parent pointers, created/deleted diff lists, reference counts, and inode maps remain coherent.

Open-file and append regressions are covered by renaming an under-construction file that exists in a snapshot and appending to a renamed snapshot file without closing it before checkpoint/restart. The tests ensure the current inode remains a `DstReference`, transitions between under-construction and closed states correctly, and can be serialized.

The final scenarios cover overwrite diff reports, double renames followed by snapshot deletion and restart, and content-summary/quota-usage equality for truncated renamed files that have become `INodeReference` instances.

## State and persistence behavior

The tests treat snapshot rename state as a persistent namespace invariant. `restartClusterAndCheckImage` compares tree dumps after both edit-log replay and fsimage loading, so failures in edit serialization, image serialization, snapshot diff order, quota persistence, or reference node reconstruction are caught.

State transitions under scrutiny include:

- Normal inode to inode-with-snapshot conversion after snapshot-protected mutation.
- Current moved inode represented as `DstReference`, old snapshot entry represented as `WithName`, and shared identity held through `WithCount`.
- `ChildrenDiff` created/deleted list changes for moved, created, overwritten, or deleted nodes.
- `FileDiff` and `DirectoryDiff` snapshot IDs after cross-directory movement and snapshot deletion.
- Namespace and storage-space quota recomputation after rename, overwrite, truncation, and snapshot cleanup.

## Dependencies and integration points

This suite integrates HDFS client APIs, NameNode namespace internals, snapshot manager behavior, block/storage quota accounting, edit-log replay, fsimage load/save, and Mockito-driven fault injection. It also depends on `SnapshotTestHelper`, `DFSTestUtil`, `GenericTestUtils`, `Whitebox`, and JUnit 5 timeouts/tags.

## Risks and maintenance notes

- The tests are slow and stateful; they restart clusters repeatedly and compare dumped trees, so failures can be expensive but usually high signal.
- Several tests assert exact reference counts, diff counts, snapshot IDs, and exception messages. They are sensitive to internal representation changes even when public behavior remains compatible.
- Forced failure tests use Mockito and `Whitebox.setInternalState` against NameNode internals, which can break during refactors.
- Some quota checks intentionally disable quota comparison after known quota-usage movement subtleties; future quota fixes should revisit these assertions.
- Rename across nested or overlapping snapshottable directories is a fragile area; these tests encode unsupported-case error messages and supported nested-snapshot toggles.

## Test signals

Strong signals include public snapshot path existence, `SnapshotDiffReport` content, `INodeReference` class and reference count checks, exact `DirectoryDiff` and `FileDiff` snapshot IDs, quota/content-summary equality, successful checkpoint/restart, and correct exceptions for forbidden operations. The highest-value regression coverage is around rename undo, snapshot deletion diff combination, open-file persistence, overwrite reports, and cross-snapshottable-directory reference cleanup.

# Research group subset-b-007560

Work item: `subset-b-007560`

Scope: six HDFS snapshot test sources under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRenameWithSnapshots.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRenameWithSnapshots.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSetQuotaWithSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSetQuotaWithSnapshot.java

## Purpose

`TestSetQuotaWithSnapshot` verifies how HDFS quota operations interact with snapshottable directories and descendants that have snapshot diffs. It is a focused integration test around preserving snapshottable metadata while setting or clearing quotas, and ensuring quota clearing does not disturb snapshot diff state.

## Important APIs, types, and helpers

- Public APIs under test: `mkdirs`, `allowSnapshot`, `createSnapshot`, `setQuota`, `getSnapshottableDirListing`.
- Internal APIs: `FSDirectory.getINode4Write`, `INodeDirectory.isQuotaSet`, `isSnapshottable`, `isWithSnapshot`, `getDiffs`, `DirectoryDiff.getChildrenDiff`.
- Constants: `HdfsConstants.QUOTA_DONT_SET` and `HdfsConstants.QUOTA_RESET`.
- Helpers: `SnapshotTestHelper.createSnapshot`, `DFSTestUtil.createFile`, and `DFSUtil.string2Bytes`.

## Control flow

The fixture starts a formatted `MiniDFSCluster` with block size `1024` and replication `3`, then records `FSNamesystem`, `FSDirectory`, and `DistributedFileSystem`.

`testSetQuota` creates `/TestSnapshot`, creates snapshot `s1`, then creates a child directory and file after the snapshot. It asserts that the child directory is not automatically converted into an `INodeDirectoryWithSnapshot`. After `setQuota` on the child, it verifies the inode is quota-set but still not snapshot-bearing.

`testClearQuota` first marks a directory snapshottable without snapshots and calls `setQuota` with don't-set, explicit quota values, and reset values. Each operation must keep the directory snapshottable and must not create diffs. After snapshot creation, quota reset must preserve the snapshottable directory listing and existing diff count. The test then creates a subdirectory, takes a second snapshot, creates a file after that snapshot, clears quota again, and verifies the subdirectory carries a single `DirectoryDiff` for snapshot `s2` whose created list contains the current file inode.

## State and persistence behavior

This file does not restart the cluster or explicitly save fsimage. Its state assertions are in-memory NameNode namespace invariants. The important persistence-adjacent signal is that quota feature changes must not rewrite snapshottable identity or disturb existing diff lists, because those are serialized by the broader NameNode snapshot machinery.

## Dependencies and integration points

The test ties together client quota calls, snapshot manager snapshottable listings, `INodeDirectory` quota features, and directory diff tracking. It depends on the internal distinction between snapshottable directories, directories with snapshot diffs, and quota-set directories.

## Risks and maintenance notes

- The test asserts internal diff list sizes and exact created-list identity with `assertSame`, so internal representation refactors can require test updates.
- It uses boundary-ish quota constants (`QUOTA_DONT_SET - 1`) to validate API interpretation; changes to quota constants or validation semantics should be reviewed here.
- It does not check edit-log/fsimage persistence directly; regressions that appear only after restart are covered elsewhere.

## Test signals

Key signals are `isQuotaSet`, `isWithSnapshot`, `isSnapshottable`, diff-list sizes, snapshottable directory listing contents, snapshot ID matching for `s2`, and object identity between the created diff entry and the live `INode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSetQuotaWithSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapRootDescendantDiff.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapRootDescendantDiff.java

## Purpose

`TestSnapRootDescendantDiff` verifies snapshot diff-report rejection for descendant directories when the configuration disallows computing diffs from non-snapshot-root descendants. It is a narrow regression test for `getSnapshotDiffReport` validation under `DFS_NAMENODE_SNAPSHOT_DIFF_ALLOW_SNAP_ROOT_DESCENDANT=false`.

## Important APIs, types, and helpers

- Configuration keys: `DFS_NAMENODE_SNAPSHOT_CAPTURE_OPENFILES`, `DFS_NAMENODE_ACCESSTIME_PRECISION_KEY`, `DFS_NAMENODE_SNAPSHOT_SKIP_CAPTURE_ACCESSTIME_ONLY_CHANGE`, and `DFS_NAMENODE_SNAPSHOT_DIFF_ALLOW_SNAP_ROOT_DESCENDANT`.
- Public APIs under test: `mkdirs` and `getSnapshotDiffReport`.
- Helper flow: `modifyAndCreateSnapshot` delegates to `TestSnapshotDiffReport.modifyAndCreateSnapshot` and a local snapshot-name generator.
- Assertion helper: `GenericTestUtils.assertExceptionContains`.

## Control flow

The test cluster enables snapshot open-file capture and access-time filtering but explicitly disables descendant diff support. The test creates `/TestSnapRootDescendantDiff/sub1/subsub1/subsubsub1`, creates snapshots on `sub1` while modifying both the snapshot root and a deeper descendant, then attempts to call `getSnapshotDiffReport` on `subsub1` between `s1` and `s2`.

The expected result is an `IOException` whose message says the descendant path is not a snapshottable directory. This confirms that when descendant diff support is disabled, only the snapshottable root is accepted as the diff-report root.

## State and persistence behavior

The file does not test persistence or edit-log replay. The state under test is transient NameNode validation state: the snapshot root exists and has snapshots, but the descendant directory does not gain snapshottable status merely because it lies under the snapshot root.

## Dependencies and integration points

This test integrates snapshot-diff configuration, `DistributedFileSystem.getSnapshotDiffReport`, snapshot creation via `TestSnapshotDiffReport`, and NameNode path validation. It depends on error semantics distinguishing "descendant of a snapshottable root" from "snapshottable directory".

## Risks and maintenance notes

- If descendant snapshot diff support becomes enabled by default or validation messages are changed, this test will need adjustment.
- The local snapshot-name map starts at `s0` per snapshot directory and relies on `TestSnapshotDiffReport.modifyAndCreateSnapshot` creating a predictable sequence.
- Because the test only validates the disabled path, enabled descendant-diff behavior must be covered elsewhere.

## Test signals

The primary signal is the precise exception content for `subsub1`. Secondary signals are successful snapshot creation and mutation setup under the configured diff constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapRootDescendantDiff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshot.java

## Purpose

`TestSnapshot` is the broad snapshot functionality suite for HDFS. It combines a randomized, multi-iteration invariant test over generated directory trees with targeted tests for snapshot creation, illegal names, snapshottable permissions, metadata timestamps, reserved raw paths, offline image viewing, and fsimage/edit-log consistency.

## Important APIs, types, and helpers

- Public APIs under test: `allowSnapshot`, `disallowSnapshot`, `createSnapshot`, `deleteSnapshot`, `renameSnapshot`, `setTimes`, `setPermission`, `setOwner`, `setReplication`, `append`, `delete`, `mkdirs`, `saveNamespace`, and safe mode controls.
- Snapshot model helpers: `SnapshotTestHelper.TestDirectoryTree`, `SnapshotTestHelper.createSnapshot`, `checkSnapshotCreation`, `getSnapshotFile`, `dumpTree2File`, and `compareDumpedTreeInFile`.
- Persistence and tooling: `FSImageTestUtil.findLatestImageFile`, `PBImageXmlWriter`, `MiniDFSCluster` restart flows.
- Inner modification hierarchy: `Modification`, `FileStatusChange`, `FileChangePermission`, `FileChangeReplication`, `FileChown`, `FileAppend`, `FileAppendNotClose`, `FileAppendClose`, `FileCreation`, `FileDeletion`, `DirCreationOrDeletion`, and `DirRename`.

## Control flow

The fixture starts a three-datanode `MiniDFSCluster`, creates a `TestDirectoryTree` of height `5`, and records namespace internals. The main `testSnapshot` runs `runTestSnapshot(20)`.

Each randomized iteration enables nested snapshots, creates one snapshot on the tree root and one on a random directory, prepares modifications for the snapshot roots plus an additional random directory, applies each modification, and verifies all previously recorded snapshots still expose the same status, length, and existence as before the modification. It then applies random chmod and chown operations to directories and calls `checkFSImage`.

`checkFSImage` dumps the namespace tree, restarts without formatting to validate edit-log replay, saves namespace in safe mode, restarts again to validate fsimage load, and compares all dumped trees. `testOfflineImageViewer` runs one snapshot iteration, finds the latest protobuf fsimage, and verifies `PBImageXmlWriter` can parse it.

Targeted tests cover:

- Updating a subdirectory mtime under a snapshotted parent while the snapshot copy retains old times.
- Illegal snapshot names including `.snapshot`, absolute paths, path separators, and nested names.
- Attempts to create/delete/rename snapshots on non-snapshottable directories.
- Idempotence of `allowSnapshot` and `disallowSnapshot`, including root's special snapshottable-with-zero-quota behavior.
- Snapshot mtime stability across restart, mtime change after rename, and directory mtime persistence after snapshot deletion.
- Snapshot operations through `/.reserved/raw` paths, including root-level raw paths, followed by NameNode restart.

The inner modification classes load snapshot state, mutate current files/directories, then check snapshots. Status-changing classes compare full `FileStatus.toString()`. Append checks snapshot lengths and reads at the old boundary to ensure EOF. Creation/deletion and directory operations verify snapshot file existence and child status snapshots.

## State and persistence behavior

Persistence is a primary concern. The main loop repeatedly verifies both edit-log replay and fsimage save/load after many snapshot and mutation combinations. It also validates offline fsimage parsing and raw reserved path edit replay.

State tracked by the suite includes snapshot root lists, snapshot file mappings, file status snapshots, file lengths, directory child status, open append streams, and the generated directory tree's current non-snapshot children. The invariant is that current-tree mutations must not alter any existing snapshot view.

## Dependencies and integration points

This file integrates the HDFS client API, NameNode namespace internals, fsimage/edit-log persistence, offline image viewer, reserved raw path handling, directory tree test helpers, and randomized mutation generation. It depends on deterministic snapshot-path mapping through `SnapshotTestHelper` even while the current tree changes.

## Risks and maintenance notes

- The test is randomized using `Time.now()` as seed and logs the seed. Failures may require reproducing with the printed seed if behavior is order-sensitive.
- The global static `snapshotList` and counters make per-test lifecycle assumptions important.
- Comparing `FileStatus.toString()` is intentionally stronger than `equals`, but can be sensitive to harmless formatting changes.
- The open append sequence depends on `hsync(UPDATE_LENGTH)` and close ordering.
- Broad slow tests can mask which exact mutation caused failure unless the printed modification count and dump output are used.

## Test signals

Signals include snapshot existence checks, immutable `FileStatus` and length comparisons, EOF reads at snapshot boundaries, exact exception messages for invalid APIs, root snapshot quota values, mtime equality/inequality, successful offline image parsing, and dump-tree equality after edit replay and fsimage load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotBlocksMap.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotBlocksMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotDeletion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotDeletion.java

## Purpose

`TestSnapshotDeletion` is the broad regression suite for deleting snapshots and snapshot-protected current namespace entries. It validates deletion refusal rules, edit-log replay, quota accounting, block cleanup, diff-list combination, permission-disabled deletion, HA restart, fsimage corruption regressions, rename/delete cleanup, concat interactions, and snapshot diff reports after concat.

## Important APIs, types, and helpers

- Public APIs under test: `delete`, `deleteSnapshot`, `createSnapshot`, `allowSnapshot`, `setQuota`, `setReplication`, `setOwner`, `rename`, `concat`, `getSnapshotDiffReport`, `saveNamespace`, and `FsShell -deleteSnapshot`.
- Internal APIs: `FSDirectory`, `INodeDirectory`, `INodeFile`, `DirectoryDiffList`, `QuotaCounts`, `BlockInfo`, `BlockManager`, `BlockManagerTestUtil`, and inode-map lookups by ID.
- Helpers: `getDir`, `checkQuotaUsageComputation`, `SnapshotTestHelper.createSnapshot`, `getSnapshotPath`, and `TestSnapshotBlocksMap.assertBlockCollection`.
- HA/persistence tools: `MiniDFSNNTopology.simpleHATopology`, `HATestUtil.configureFailoverFs`, `NameNodeAdapter.abortEditLogs`, `rollEditLog`, safe mode, and namespace save/restart.

## Control flow

The fixture starts a formatted three-datanode cluster and records namespace and block manager handles. Many tests create `/TestSnapshot/sub1/subsub1` as the base tree.

Deletion guard tests assert that deleting a snapshottable directory with snapshots, or an ancestor of a snapshottable descendant with snapshots, fails with a clear `RemoteException`. `testApplyEditLogForDeletion` verifies that deleting snapshottable directories without snapshots updates the snapshot manager list after edit-log replay and after fsimage save/load.

`testDeleteCurrentFileDirectory` is the largest current-tree deletion scenario. It deletes normal files/directories before snapshots, deletes created-after-snapshot content, creates multiple snapshots, changes replication, deletes subtrees, then verifies quota, block invalidation, snapshot subtree shape, parent pointers, child lists for different snapshot IDs, and file replication in snapshot copies.

Earliest snapshot deletion tests cover deleting nonexistent snapshots, deleting and recreating snapshot names, preserving later snapshot file status, combining the first directory and file diffs, cleaning deleted-file blocks, and removing obsolete diffs while keeping no-change nodes in the current tree.

Diff-combination tests create sequences where files are deleted, recreated, modified, or created between snapshots `s1`, `s2`, and `s3`. Deleting middle snapshots must merge or destroy entries correctly, preserve status in older snapshots, drop created-after-prior files, and update quota/storage-space counts. Variants place modifications at the root of the snapshot and deeper in the subtree.

Later tests cover directory metadata diffs, deleting snapshots when permissions are disabled via a different user, renaming a snapshot diff to its previous snapshot under nested snapshots, illegal `FsShell -deleteSnapshot` arguments, HA NameNode restart after `OP_DELETE_SNAPSHOT`, zero-block totals after restart, HDFS-9697 fsimage corruption, moving a snapshot-protected file outside the snapshottable tree and deleting it, and concat behavior.

Concat tests assert that concat fails when a source is in a snapshot, that repeated concat plus snapshot deletion survives save/restart, and that snapshot diff reports show a single `MODIFY` entry on the concat destination.

## State and persistence behavior

This file repeatedly checks three state planes:

- Namespace state: current inodes, snapshot copies, directory diff lists, metadata copies, parent/child relationships, and inode-map cleanup.
- Quota and block state: namespace/storage-space counts from both stored quota features and recomputation, block collection invalidation, block totals after restart, and marked-delete queue draining.
- Persistence state: edit-log replay after deletion, fsimage save/load, HA active restart after aborted edit logs, and fsimage corruption regressions.

`checkQuotaUsageComputation` is central: it compares stored `DirectoryWithQuotaFeature` usage with freshly computed quota usage and emits dump-tree context on mismatch.

## Dependencies and integration points

The suite integrates snapshot deletion with NameNode snapshot manager lists, directory/file diff algorithms, block manager cleanup, quota accounting, command-line `FsShell`, permissions, HA failover plumbing, concat semantics, snapshot diff reports, and fsimage/edit-log persistence.

## Risks and maintenance notes

- Many tests assert exact quota numbers and diff-list sizes. These are strong regression signals but can be brittle during internal accounting refactors.
- Some tests rely on exact exception message fragments and shell output text.
- HA and restart tests are slow and can expose timing sensitivity; one test waits for asynchronous block deletion.
- The concat scenarios use randomized file seeds and repeated recreate/concat cycles to stress diff state.
- Permission-disabled deletion uses `UserGroupInformation.doAs` and expects no authorization failure when permissions are globally disabled.

## Test signals

High-value signals include deletion refusal messages, snapshot manager counts after restart, quota stored-vs-computed equality, block collection IDs becoming invalid only when safe, snapshot path presence/absence, metadata owner/group and replication values in snapshots, diff-list snapshot IDs, inode-map cleanup after rename/delete, zero total blocks after restart, successful fsimage save/restart, shell argument errors, HA restart completion, and concat diff-report contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotDeletion.java -->

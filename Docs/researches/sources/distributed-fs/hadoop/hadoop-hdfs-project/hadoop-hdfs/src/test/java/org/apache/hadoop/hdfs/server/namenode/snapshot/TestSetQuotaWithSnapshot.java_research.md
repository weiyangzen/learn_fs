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

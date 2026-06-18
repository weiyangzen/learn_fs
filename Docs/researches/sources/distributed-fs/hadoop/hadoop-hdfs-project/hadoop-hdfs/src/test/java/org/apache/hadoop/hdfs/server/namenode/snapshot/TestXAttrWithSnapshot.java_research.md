# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestXAttrWithSnapshot.java

## Purpose
`TestXAttrWithSnapshot` verifies extended attribute behavior for snapshot roots and snapshot paths. It ensures snapshots preserve xattr point-in-time values, live changes read current state, snapshot paths are read-only for xattr mutation, xattrs survive edit-log and checkpoint restarts, and shell copy with `-px` preserves snapshot xattrs.

## Important APIs, Types, and Functions
The file uses `DistributedFileSystem.setXAttr/getXAttrs/removeXAttr`, `XAttrSetFlag`, `SnapshotTestHelper.createSnapshot`, `SnapshotAccessControlException`, `SnapshotDiffReport`, `SafeModeAction`, `NameNodeAdapter.saveNamespace`, `FsShell`, `ToolRunner`, and `DFS_NAMENODE_XATTRS_ENABLED_KEY`. Shared helpers include `doSnapshotRootChangeAssertions`, `doSnapshotRootRemovalAssertions`, `initCluster`, and `restart`.

## Control Flow
The class starts one static cluster with xattrs enabled and allocates a unique `/pN` path per test. It tests xattrs added after snapshot creation do not appear in the earlier snapshot, modified/removed live xattrs do not mutate captured snapshot values, restart with and without checkpoint preserves divergent live/snapshot xattr state, successive snapshots capture each version independently and deleting one snapshot does not corrupt others, snapshot paths reject `setXAttr` and `removeXAttr`, and `FsShell -cp -px` copies snapshot xattrs to a new live path.

## State and Persistence Behavior
This suite strongly covers persisted namespace state. `restart(false)` replays edits, while `restart(true)` saves namespace before cluster restart. `testXattrWithSnapshotAndNNRestart` explicitly enters safe mode, saves namespace, restarts, and verifies snapshot diff remains empty after xattrs set before snapshot creation.

## Dependencies and Integration Points
It integrates xattr storage, snapshot copy-on-write metadata, snapshot diff calculation, safe-mode namespace save, NameNode restart, snapshot access control, and shell copy preservation flags.

## Risks and Edge Cases
Risks include xattr changes accidentally modifying snapshot roots, snapshot xattrs not surviving fsimage/edit replay, read-only snapshot path mutation being allowed, deleted snapshots corrupting retained xattr diffs, and shell copy ignoring xattrs. Because the cluster is static, test isolation depends on unique path names and proper cluster reinitialization after restarts.

## Test Signals
Signals are exact xattr map sizes and byte-array values, expected `SnapshotAccessControlException`, empty snapshot diff assertions, successful shell return code, and repeated assertions after both edit-log and checkpoint restarts.

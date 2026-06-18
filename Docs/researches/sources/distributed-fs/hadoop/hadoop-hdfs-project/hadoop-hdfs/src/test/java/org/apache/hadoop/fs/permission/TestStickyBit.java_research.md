# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/permission/TestStickyBit.java

## Purpose

`TestStickyBit` verifies HDFS sticky-bit behavior under normal permission checks and ACL-enabled paths. It uses a `MiniDFSCluster` with permissions and NameNode ACLs enabled, then exercises Unix-like sticky semantics: non-owners may append to writable files, but may not delete or rename another user's child under a sticky directory. It also checks sticky-bit propagation, reset semantics, recursive delete enforcement, and persistence across NameNode restart.

## Important APIs, types, and functions

The class centers on `MiniDFSCluster`, `DistributedFileSystem`, `FileSystem`, `FsPermission`, `AclEntry`, `UserGroupInformation`, `AccessControlException`, and `FSExceptionMessages.PERMISSION_DENIED_BY_STICKY_BIT`. Key helpers are `initCluster(boolean)`, `confirmCanAppend`, `confirmDeletingFiles`, `confirmStickyBitDoesntPropagate`, `confirmSettingAndGetting`, `testMovingFiles(boolean)`, `writeFile`, and `applyAcl`.

## Control flow, state, and persistence

`@BeforeAll` creates a four-DN cluster and user-scoped file systems for `theDoctor` and `rose`; `@BeforeEach` cleans root children. The main behavior tests create paths, set octal permissions such as `01777`, then perform operations as owner and non-owner users. Persistence tests set permissions, shut down the cluster, restart without formatting, and verify sticky bits survive edit/fsimage replay while absent bits remain absent. Recursive-delete tests verify sticky checks are enforced while walking children.

## Dependencies and integration points

The test integrates HDFS permission enforcement, `DFS_PERMISSIONS_ENABLED`, `DFS_NAMENODE_ACLS_ENABLED`, ACL storage, edit-log/fsimage persistence, and UGI-based client identity. It also relies on `DFSTestUtil.getFileSystemAs` to bind clients to distinct users.

## Risks and test signals

Regressions would allow unauthorized deletes/renames, incorrectly block file appends, propagate sticky bits to new subdirectories, lose the bit after restart, or produce weak exception diagnostics. Strong signals are expected `AccessControlException` messages containing "sticky bit", user, path, and parent, plus correct `FsPermission.getStickyBit()` values before and after restart.

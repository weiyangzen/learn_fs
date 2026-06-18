# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestPermissionSymlinks.java

## Purpose
This class validates HDFS permission and ACL behavior for symlink operations. It checks that deleting and renaming a link depend on link-parent permissions, reading/accessing a link depends on target permissions, and link status/target inspection does not require target read permission.

## Important APIs, types, and functions
- Static paths define `/symtest1/link` pointing to `/symtest2/target`.
- Class setup enables HDFS permissions and ACLs, starts a MiniDFSCluster, and creates a `FileSystemTestWrapper`.
- Per-test setup creates link and target; per-test teardown deletes both parent directories.
- Helper methods implement repeated checks for delete, read, link-status, and rename behavior through `FileContext` and `FileSystem`.

## Control flow
Each test configures permissions or ACLs, then invokes a helper under a non-superuser `UserGroupInformation.doAs`. Delete tests ensure non-writable link parent blocks link deletion, while non-writable target parent/target does not block deleting only the link. Read tests deny opening the symlink when target read is denied. Link-status tests allow `getFileLinkStatus` and `getLinkTarget` despite target read denial. Rename tests separately cover FileContext `rename(..., Rename.NONE)` and FileSystem `rename`, allowing rename when only target is unwritable and denying when source link parent is unwritable. `testAccess` checks `FileContext.access` through a symlink and validates an error message for a bad child path through a non-directory target.

## State and persistence behavior
The cluster is shared per class. Each test recreates the same symlink and target and removes them afterward. ACL and permission mutations are local to those paths and cleared by directory deletion.

## Dependencies and integration points
The test integrates HDFS symlink implementation, `FileContext`, `FileSystem`, ACL helpers from NameNode tests, `FsPermission`, `FsAction`, `FileSystemTestWrapper`, non-superuser UGI, and `GenericTestUtils.assertExceptionContains`.

## Risks and edge cases
Because it uses a shared static cluster, failed cleanup can affect later tests. ACL tests rely on exact effective permissions for a named user. Error-message assertions in `testAccess` intentionally check that the resolved target path appears and the unresolved bad symlink path does not.

## Test signals
Passing confirms symlink operations enforce permissions on the correct inode/path: link-parent write for delete/rename, target permissions for dereferenced read/access, and non-dereferencing status operations independent of target readability.

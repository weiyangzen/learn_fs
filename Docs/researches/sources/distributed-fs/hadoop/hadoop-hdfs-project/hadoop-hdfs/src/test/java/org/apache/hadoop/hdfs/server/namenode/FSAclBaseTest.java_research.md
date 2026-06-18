# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSAclBaseTest.java

## Purpose
`FSAclBaseTest` is an abstract JUnit base suite for HDFS NameNode ACL semantics. It tests every major ACL mutation API, interaction with permission bits, default ACL inheritance, restart persistence, permission enforcement, effective access masks, and internal `AclFeature` deduplication/reference counting.

## Important APIs, Types, and Functions
- Static users `BRUCE`, `DIANA`, `BOB`, and `SUPERGROUP_MEMBER` model owner, non-owner, grouped user, and supergroup access.
- `startCluster()` enables `DFS_NAMENODE_ACLS_ENABLED_KEY` and starts a 1-DataNode `MiniDFSCluster`.
- Per-test `setUp()` creates a fresh path `/pN` and filesystem handles for each user; `destroyFileSystems()` closes them.
- Test groups cover `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `setPermission`, default ACL inheritance on new files/dirs/intermediate paths/symlinks, rename behavior, authorization checks, `FileSystem.access`, effective permissions, and deduplication.
- Helpers include `restartCluster()`, `assertAclFeature(...)`, `getAclFeature(...)`, and `assertPermission(...)`.

## Control Flow and Behavior
Mutation tests generally create a file or directory, set initial permissions and ACLs, call one ACL API, fetch `AclStatus`, compare exact returned ACL entries, assert extended permission bits, and inspect whether the backing inode has an `AclFeature`. Negative cases assert `FileNotFoundException` or `AclException` for missing paths and default ACLs on files. Sticky-bit tests verify ACL operations preserve sticky mode bits.

Inheritance tests set default ACLs on parent directories and then create child files, directories, intermediate paths, and symlinks. They verify that child files receive access ACLs when needed, child directories receive both access and default ACLs, minimal defaults can collapse to no `AclFeature` for files, access-only ACLs are not inherited, and renaming into an ACL-bearing directory does not apply inherited defaults retroactively. UMask tests toggle `FSDirectory.setPosixAclInheritanceEnabled` to compare legacy and POSIX ACL inheritance behavior.

Authorization tests create resources as `bruce`, then verify only owner, superuser, or supergroup members can mutate ACLs or read ACL status across traverse restrictions. Access tests check named user and named group precedence, including a named user deny overriding group grants. Effective-access tests validate that `AclStatus.getEffectivePermission` reflects the current mask after `setPermission`.

`testDeDuplication` restarts the cluster for a clean static `AclStorage` map, creates identical inherited ACLs across siblings and files, verifies reference-count reuse, verifies counts decrease on ACL mutation/removal/deletion, and checks behavior after loading edits and fsimage by restarting the NameNode and saving namespace.

## State and Persistence
The suite creates persistent HDFS namespace ACL metadata and repeatedly restarts clusters without formatting to verify edit-log/fsimage persistence. It also inspects internal inode state through `FSDirectory.getINode(..., DirOp.READ_LINK)` and `INode.getAclFeature`. Static `AclStorage.getUniqueAclFeatures()` is explicitly cleared for dedup tests. Configuration flags for permissions and POSIX ACL inheritance are temporarily changed and restored.

## Dependencies and Integration Points
The class depends on `MiniDFSCluster`, `FileSystem`, `DFSTestUtil`, `AclTestHelpers`, `AclStorage`, `AclFeature`, `FSDirectory`, `INode`, `FsPermissionExtension`, `AclStatus`, HDFS safe mode/saveNamespace RPCs, and Hadoop security `UserGroupInformation`. Subclasses provide concrete cluster initialization through this abstract base pattern.

## Risks and Edge Cases
- Many tests compare exact ACL entry arrays; ordering or canonicalization changes will break them.
- Static cluster/configuration/path state means subclasses must coordinate setup correctly.
- `testDeDuplication` manipulates static global ACL feature intern tables and has comments noting reference counts differ after restart within the same JVM.
- Permission bit assertions use extended ACL-bit encoding, so expected octal values are subtle.
- Tests that restart clusters and save namespaces are heavier and can expose unrelated MiniDFSCluster timing issues.

## Test Signals
Signals include exact `AclStatus` entry arrays, `FileStatus.hasAcl`, permission shorts, direct `AclFeature` presence/absence and immutable entries, restart-stable ACL lists, expected `AccessControlException`, successful/failed `FileSystem.access`, and deduplicated `AclFeature` unique-element counts and reference counts.

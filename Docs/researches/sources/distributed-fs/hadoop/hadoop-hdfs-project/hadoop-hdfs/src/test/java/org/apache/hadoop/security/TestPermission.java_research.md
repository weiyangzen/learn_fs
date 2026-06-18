# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/security/TestPermission.java

## Purpose
`TestPermission` validates HDFS permission and ownership semantics: umask compatibility, directory/file creation permissions, default permissions, read/write/execute bits, access-control failures, rename checks, and `setOwner` rules for superusers and non-superusers.

## Important APIs, types, and functions
- Static helpers `checkPermission`, `createFile`, `canMkdirs`, `canCreate`, `canOpen`, and `canRename` centralize file creation and expected access-control behavior.
- `testBackwardCompatibility()` checks old/new umask configuration parsing, including invalid umasks.
- `testCreate()` checks mkdir/create permission propagation, inherited parent permissions, umask behavior, and `FileSystem.mkdirs/create` static helpers.
- `testFilePermission()` performs the broader integration scenario using NameNode file system and a non-superuser file system.
- Private ownership tests cover superuser owner/group changes and non-superuser allowed/denied group/owner changes.

## Control flow
`testCreate` starts a MiniDFSCluster with permissions enabled and umask `000`, creates nested directories and files with explicit permissions, switches umask to `022`, and verifies status permissions. `testFilePermission` starts another cluster, validates non-existent file errors, creates files/dirs, writes and reads random bytes, changes permission bits, creates a non-superuser UGI, attempts denied operations, relaxes permissions to permit rename, then runs owner/group subtests.

## State and persistence behavior
Tests persist files under `/data` and root-level helper paths inside MiniDFSCluster. Randomized user names avoid collisions. Instance fields `nnfs` and `userfs` hold superuser and non-superuser file-system handles during `testFilePermission`. Clusters are shut down in `finally` blocks.

## Dependencies and integration points
This class integrates `FsPermission`, HDFS permission enforcement, `MiniDFSCluster`, `DFSTestUtil.getFileSystemAs`, `UserGroupInformation`, `AccessControlException`, and AssertJ/JUnit assertions. It checks both API return behavior and error-message path contents.

## Risks and edge cases
Some assertions use string forms of permissions, so changes in display formatting could break tests. `testNonSuperCannotChangeOwnerForNonExistentFile` accepts either `AccessControlException` or `FileNotFoundException`, reflecting implementation variability. Random user naming is helpful but can make logs non-deterministic.

## Test signals
Passing confirms HDFS permission bits and umasks are applied correctly, permission-denied messages include absolute paths, non-superusers cannot bypass ownership/group restrictions, and superusers retain owner/group mutation powers.

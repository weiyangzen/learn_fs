# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestExtendedAcls.java

## Purpose
Tests HDFS extended ACL inheritance and access enforcement for directories and files. The suite focuses on default ACL propagation, immutability of already-created children when parent defaults change, non-inheritance of access ACLs, granting extra access in subdirectories, and restricting inherited access in subdirectories.

## Important APIs and Types
Uses `setAcl`, `modifyAclEntries`, `removeAcl`, `getAclStatus`, `setPermission`, `access`, `UserGroupInformation.doAs`, `AclEntry`, `AclStatus`, `FsPermission`, and `FsAction`. Helpers come from `AclTestHelpers.aclEntry`.

## Control Flow
`setup()` enables NameNode ACL support and starts a three-DataNode cluster. `testDefaultAclNewChildDirFile` sets a parent default ACL and verifies new directories receive access plus default ACL entries while new files receive access entries. `testDefaultAclExistingDirFile` shows existing children retain old inherited ACLs after parent ACL changes/removal. `testAccessAclNotInherited` confirms only default ACLs propagate. `testGradSubdirMoreAccess` adds a group default ACL to a child directory and verifies group access only below that child. `testRestrictAtSubDir` changes a child default ACL to deny a group and verifies parent access remains broader than child access. `tryAccess` impersonates users and maps `AccessControlException` to boolean results.

## State, Persistence, Dependencies, Integration
State is ACL entries on inodes, permission bits and masks, generated child ACLs, and user/group identity in UGI. The tests do not restart the cluster, so persistence to fsimage/edit logs is not covered here. Integration points are NameNode ACL evaluation, filesystem metadata mutation, and access checks through impersonated clients.

## Risks and Test Signals
Signals are exact ACL entry arrays and boolean access decisions for named users/groups. Risks include brittleness to ACL entry ordering and mask-calculation changes, but exact ordering is part of the current returned `AclStatus` contract these tests protect.

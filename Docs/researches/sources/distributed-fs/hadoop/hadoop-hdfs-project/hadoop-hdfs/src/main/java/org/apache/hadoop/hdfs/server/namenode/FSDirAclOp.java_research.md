# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAclOp.java

## Purpose
`FSDirAclOp` contains static helper operations for NameNode ACL mutation and retrieval on inodes. It is the FSDirectory-facing implementation behind client ACL APIs.

## Important APIs and Types
Operations include `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `getAclStatus`, `unprotectedSetAcl`, and private config/removal helpers. It uses `AclStorage`, `AclTransformation`, `AclFeature`, `AclEntry`, `AclStatus`, `FsPermission`, and FSDirectory path resolution.

## Control Flow
Mutating methods first check that ACLs are enabled, take the FSDirectory write lock, resolve the path for write, check owner, compute transformed ACL entries, update inode ACL state with the latest snapshot ID, log `OP_SET_ACL`, and release the lock. `removeAcl` uses `unprotectedRemoveAcl` and logs an empty ACL list. `getAclStatus` takes a read lock, handles `.snapshot` specially, reads inode attributes and logical ACL entries, and builds an `AclStatus`.

## State and Persistence
ACL state is stored as inode ACL features and permission bits. Persistence is through edit-log `logSetAcl` and fsimage inode serialization. Unprotected methods are intended for edit-log replay or callers already holding the write lock.

## Dependencies and Integration
It integrates with `FSDirectory`, permission checking, snapshots, edit logging, and HDFS ACL storage/transformation utilities.

## Risks and Test Signals
`unprotectedRemoveAcl` restores group permission bits from the ACL feature's group entry, so malformed feature ordering can trigger an index exception. `AclException` messages are augmented with path context. Tests should cover ACL disabled config, owner enforcement, default ACL removal, full ACL removal restoring group bits, `.snapshot` status, edit-log replay with `fromEdits`, and snapshot-aware ACL updates.

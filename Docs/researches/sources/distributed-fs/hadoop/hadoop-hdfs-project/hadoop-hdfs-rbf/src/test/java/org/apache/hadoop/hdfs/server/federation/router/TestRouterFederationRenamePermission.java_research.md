# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenamePermission.java

## Purpose

`TestRouterFederationRenamePermission.java` checks permission and ACL enforcement for router federation rename. It extends the shared rename base, uses a synthetic remote user `foo`, and verifies source existence, source parent permissions, ACLs, destination parent existence and ownership, successful rename, and snapshot path rejection. The source was read as a complete 246-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `UserGroupInformation`, `DFSClient`, `ClientProtocol`, `RemoteLocation`, `RouterFederationRename.checkSnapshotPath`, `FsPermission`, `AclEntry`, `AclEntryScope`, `AclEntryType`, and `FsAction`. Important methods are `testSetup`, `testRenameSnapshotPath`, `testPermission1` through `testPermission7`, and `buildAcl`.

## Control Flow

Each test sets source and destination nameservices, source/destination paths under `/d0/<method>`, creates user `foo`, and gets the current router filesystem. Snapshot tests call `checkSnapshotPath` with `.snapshot` in either source or destination and expect `IOException`. Permission tests progressively create the source, alter source parent mode or ACLs, create destination parent, and invoke `ClientProtocol.rename` as user `foo`. The last case grants source ACL, creates and transfers destination parent ownership to `foo`, performs rename, and verifies the moved child file.

## State and Persistence Behavior

State is transient in the mini-cluster filesystems and router permissions model. The test mutates ACLs, owners, and modes on source and destination parents. The inherited base resets locations/files for each method and tears down the shared cluster at class end.

## Dependencies and Integration Points

The file integrates HDFS ACL semantics, user/group mapping from the base class, router-side federation rename prechecks, `RemoteException` propagation, and snapshot path validation independent of live cluster state.

## Risks and Edge Cases

The tests assert specific exception class-name fragments inside `RemoteException`, so changes in wrapped exception text may break them. ACL construction deliberately includes unnamed user and group entries plus a named user; missing mask behavior is not separately tested. Only classic `rename` is used in permission cases, not `rename2`.

## Test Signals

Expected signals are `FileNotFoundException` for absent source or destination parent, `AccessControlException` for insufficient source/destination permissions, `IOException` for snapshot paths, and final successful rename when ACL and destination ownership allow it.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLoggerWithCommands.java

## Purpose

`TestAuditLoggerWithCommands` is a broad command-name coverage suite for NameNode audit logging. It verifies that successful and failed administrative, namespace, cache, snapshot, xattr, delegation-token, safe-mode, reconfiguration, and storage-management operations emit audit entries with the intended `cmd=` value and allowed flag.

## Important APIs, Types, and Functions

The fixture builds a secure/permission-enabled `MiniDFSCluster` with ACLs, delegation-token always-use, and service authorization enabled. It creates two test users, captures `FSNamesystem.AUDIT_LOG`, keeps `NamenodeProtocols proto`, and uses `DFSTestUtil.getFileSystemAs`. Important helpers are `verifyAuditLogs(String)`, `verifyAuditLogs(boolean, String)`, `verifySetQuota`, safe-mode helpers, restore-failed-storage helpers, and `removeExistingCachePools`. The tests call `DistributedFileSystem`, `FileSystem`, `NameNodeRpcServer`, `FSNamesystem`, and delegation-token APIs.

## Control Flow

Each test arranges namespace or administrative state, performs one operation as an unauthorized or authorized user, catches the expected `AccessControlException` or `IOException`, and validates the last audit log line with a regex. For many operations it closes a `FileSystem` and reruns the call to ensure client-side closed-filesystem failures do not produce new audit entries. RPC-administrative tests synthesize `Server.Call` with a remote user and mark invocations as external so `FSNamesystem` permission checks and audit paths are exercised for admin commands.

## State and Persistence Behavior

The suite mutates namespace permissions, ownership, snapshots, cache pools/directives, encryption-zone lookup inputs, delegation token lifecycle, rolling-upgrade metadata, safe-mode state, edit-log roll state, failed-storage setting, and datanode reports. State is per-test cluster state and cleaned up in `tearDown` by clearing `Server.getCurCall`, closing filesystems, and shutting down the cluster. Delegation-token tests persist token state only within the running cluster and assert audit events for get/renew/cancel success and failure.

## Dependencies and Integration Points

The file integrates with HDFS permission checking, cache manager RPCs, snapshot manager, delegation-token secret manager, NameNode admin RPC server, `FSNamesystem` admin methods, `Server.Call` IPC context, `RPC.RpcKind`, `DatanodeStorageReport`, and audit text formatting. It also uses Mockito spies to control remote users and external-invocation flags.

## Risks and Edge Cases

The test suite is sensitive to exact command names such as `contentSummary`, `setQuota`, `createSnapshot`, `addCache`, `safemode_force_exit`, `getDatanodeStorageReport`, and `reportBadBlocks`. Audit-count assertions can break if new audit events are added to failure paths. Tests that close filesystems deliberately distinguish server-side authorization logging from local client failures. Synthetic `Server.Call` setup must be kept in sync with IPC behavior to remain representative.

## Test Signals

Signals cover denied audit entries for content summary, quota, concat, snapshots, cache directives/pools, quota usage, EZ lookup, rename, xattr get, ACL status, and delete-root. Successful admin signals include metaSave, reconfiguration, refresh commands, rolling-upgrade query/finalize, rollEditLog, safe-mode actions, balancer bandwidth, refreshNodes, finalizeUpgrade, saveNamespace, datanode reports, restoreFailedStorage variants, and reportBadBlocks. Delegation-token signals validate success and failure audit lines for get, renew, and cancel with token source text.

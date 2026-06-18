<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterPermissionChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterPermissionChecker.java

## Purpose
`RouterPermissionChecker` adapts HDFS permission checking for router mount-table records. It checks ACL-like owner/group/other bits on `MountTable` entries and implements router superuser checks based on the active RPC caller.

## Important APIs, Types, and Functions
Constructors initialize the superclass `FSPermissionChecker` with router superuser/group and a caller UGI. `checkPermission(MountTable, FsAction)` evaluates mount-table mode bits against current user and groups. `checkSuperuserPrivilege` overrides NameNode behavior to require the RPC remote user to be the router superuser or a member of the configured supergroup.

## Control Flow
Mount-table checks short-circuit for superuser, owner permissions, group permissions, and finally other permissions for non-owner non-group callers. Failure raises `AccessControlException` with source path and requested action. Superuser checks fetch `NameNode.getRemoteUser`, reject missing UGI, compare short user name, then group set.

## State and Persistence Behavior
The checker stores immutable `superUser` and `superGroup` strings. It persists no data and reads caller/group state from `FSPermissionChecker` and `NameNode` request context.

## Dependencies and Integration Points
Dependencies include `FSPermissionChecker`, `MountTable`, `FsPermission`, `FsAction`, `UserGroupInformation`, `NameNode.getRemoteUser`, and `AccessControlException`. It is used by router admin and mount table access paths.

## Risks
Correctness depends on the current RPC context being set; missing UGI is an access denial. The owner/group/other logic does not consider extended ACLs, only `FsPermission` bits stored on mount-table entries. Supergroup membership uses the remote user's current group set.

## Test Signals
Tests should cover superuser bypass, owner/group/other allow and deny cases, default mount permission expectations, missing remote user denial, supergroup membership, and constructor behavior with explicit and current UGIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterPermissionChecker.java -->

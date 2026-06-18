# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrPermissionFilter.java

## Purpose

`XAttrPermissionFilter.java` enforces which xattr namespaces are visible or mutable through public HDFS APIs. The source was read as a complete 132-line file.

## Important APIs, Types, and Functions

The static APIs are `checkPermissionForApi(FSPermissionChecker, XAttr, boolean)`, `checkPermissionForApi(FSPermissionChecker, List<XAttr>, boolean)`, and `filterXAttrsForApi`.

## Control Flow

Permission checking allows `USER` xattrs for normal access and `TRUSTED` only for superusers, auditing superuser access via `checkSuperuserPrivilege`. `RAW` is allowed only when the path is under `/.reserved/raw`. The special security xattr `security.hdfs.unreadable.by.superuser` is allowed only without a value. All other `SECURITY` and `SYSTEM` cases are denied through `FSPermissionChecker.denyUserAccess`. Filtering mirrors the visibility rules but includes the special unreadable-by-superuser xattr.

## State and Persistence Behavior

The class is stateless. It gates access to xattrs that are persisted on inodes by `XAttrStorage` and fsimage/edit logs.

## Dependencies and Integration Points

It integrates with `FSPermissionChecker`, `XAttr`, `XAttrHelper`, `AccessControlException`, and `HdfsServerConstants.SECURITY_XATTR_UNREADABLE_BY_SUPERUSER`. It is used by xattr NameNode operations before reading or writing API-visible xattrs.

## Risks and Edge Cases

Incorrect raw-path detection can expose internal raw attributes. The special security xattr deliberately permits only a no-value form; accepting a value would change security semantics. Superuser auditing is an explicit side effect for trusted/user namespace access.

## Test Signals

Tests should cover each namespace for superuser and non-superuser, raw path and non-raw path, the unreadable-by-superuser xattr with and without value, list filtering, empty lists, and audit/deny callbacks on `FSPermissionChecker`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclStatus.java

## Purpose
Represents ACL metadata for a path, including owner, group, sticky bit, ordered ACL entries, and optional permission bits used to calculate effective ACL permissions.

## Important APIs, Types, And Functions
`Builder` collects owner/group/entries/sticky/permission. Accessors expose state. `getEffectivePermission(AclEntry)` and `getEffectivePermission(AclEntry, FsPermission)` apply mask/group permissions for access and default ACL entries.

## Control Flow
Effective permission requires either server-provided permission or caller-provided fallback. Named entries and group entries are intersected with the access group action or, for default ACLs, the penultimate ACL entry's permission. Owner and other entries return their own permission directly.

## State And Persistence
The constructor copies entries into a new list but does not wrap it unmodifiable. The object is intended immutable but exposes the internal list through `getEntries`.

## Dependencies And Integration Points
Returned by filesystem ACL APIs and consumed by shell `getfacl` for effective comments. Depends on `AclEntry`, `FsPermission`, `FsAction`, and Hadoop `Preconditions`.

## Risks
`equals`/`hashCode` ignore the `permission` field, which may surprise callers. Default effective-permission logic assumes ACL ordering and at least three entries. The mutable returned list can violate immutability expectations.

## Test Signals
Validate effective permissions for named user/group, mask, minimal/default ACLs, old NameNode fallback permission, equality behavior, and mutation attempts on `getEntries`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclUtil.java

## Purpose
Builds logical ACL lists by combining permission bits with extended ACL entries, and identifies minimal ACLs.

## Important APIs, Types, And Functions
`getAclFromPermAndEntries`, `getMinimalAcl`, and `isMinimalAcl` are the public helpers.

## Control Flow
`getAclFromPermAndEntries` emits owner from user bits, copies access extended entries until the first default entry, emits either a mask or group entry from group bits depending on whether access ACLs exist, emits other, then appends default entries. `getMinimalAcl` creates the three permission-derived access entries.

## State And Persistence
Stateless utility class.

## Dependencies And Integration Points
Used by shell `getfacl` and ACL consumers that need a full logical ACL from compact permission + extended-entry storage.

## Risks
The function assumes extended entries are ordered with all access entries before default entries. Misordered input can produce incorrect logical ACLs.

## Test Signals
Check minimal ACL, access-only extended ACLs, default-only ACLs, mixed access/default ordering, and mask/group entry selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclUtil.java -->

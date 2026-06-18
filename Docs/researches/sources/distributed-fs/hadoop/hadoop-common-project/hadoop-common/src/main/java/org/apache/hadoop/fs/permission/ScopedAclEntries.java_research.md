<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ScopedAclEntries.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ScopedAclEntries.java

## Purpose
Splits an ordered ACL entry list into access and default scopes.

## Important APIs, Types, And Functions
Constructor partitions entries. `getAccessEntries()` and `getDefaultEntries()` return the two lists. `calculatePivotOnDefaultEntries` finds the first default entry.

## Control Flow
The constructor finds the first `AclEntryScope.DEFAULT`. If none exists, all entries are access and default is empty. Otherwise entries before the pivot are access and entries from the pivot onward are default.

## State And Persistence
Stores sublist views or empty lists. There is no copying, so lists reflect the source list's backing behavior.

## Dependencies And Integration Points
Used by `AclCommands.GetfaclCommand` and any code that needs scope-specific ACL processing.

## Risks
Assumes ACLs are sorted by scope with all default entries after access entries. Misordered input leaves later access entries in the default slice. Sublist views can be affected by source-list mutation.

## Test Signals
Partition access-only, default-only, mixed ordered ACLs, empty lists, and intentionally misordered lists to document behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ScopedAclEntries.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryScope.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryScope.java

## Purpose
Defines whether an ACL entry enforces access on the owning inode or supplies defaults for children.

## Important APIs, Types, And Functions
Enum values are `ACCESS` and `DEFAULT`.

## Control Flow
No behavior beyond enum identity.

## State And Persistence
Enum constants are stable public API and appear in ACL object state and parsing/formatting.

## Dependencies And Integration Points
Used by `AclEntry`, `AclUtil`, `ScopedAclEntries`, `AclStatus`, and shell ACL commands to separate access and default ACL handling.

## Risks
Adding or renaming values would break stable ACL string and API compatibility.

## Test Signals
Verify parsing of `default:` entries and correct access/default partitioning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryScope.java -->

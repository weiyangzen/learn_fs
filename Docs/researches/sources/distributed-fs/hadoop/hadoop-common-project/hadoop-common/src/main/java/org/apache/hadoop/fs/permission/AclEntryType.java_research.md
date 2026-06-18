<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryType.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryType.java

## Purpose
Defines ACL subject classes: owner/specific user, owning/specific group, mask, and other.

## Important APIs, Types, And Functions
Enum values are `USER`, `GROUP`, `MASK`, and `OTHER`. `toStringStable()` returns the enum name; `toString()` delegates to it but is annotated unstable.

## Control Flow
No branching beyond string conversion.

## State And Persistence
Enum values are public stable API and are serialized through ACL string specs.

## Dependencies And Integration Points
Used by ACL parsing, effective-permission calculation, ACL shell output, and logical ACL assembly.

## Risks
The ordinal/name contract is relied on indirectly by parsing and stable output; changes must preserve names.

## Test Signals
Parse and format all types, especially mask and named user/group effective-permission behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryType.java -->

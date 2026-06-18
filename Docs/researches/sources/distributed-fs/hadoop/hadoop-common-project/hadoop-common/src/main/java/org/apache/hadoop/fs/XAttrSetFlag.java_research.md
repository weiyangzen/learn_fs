# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/XAttrSetFlag.java

## Purpose
Enum modeling xattr create/replace preconditions.

## Important APIs, Types, and Functions
CREATE and REPLACE values carry short flags; validate(String, boolean, EnumSet<XAttrSetFlag>).

## Control Flow
validate requires a non-empty flag set. If the xattr exists, REPLACE must be present; if absent, CREATE must be present.

## State and Persistence Behavior
No mutable state. Persistent effect occurs in callers that perform xattr mutation after validation.

## Dependencies and Integration Points
Integrated with FileSystem xattr setters and NameNode-side xattr handling.

## Risks and Test Signals
Tests should cover create-only, replace-only, both flags, null/empty flags, and exception message paths for existing/non-existing attributes.

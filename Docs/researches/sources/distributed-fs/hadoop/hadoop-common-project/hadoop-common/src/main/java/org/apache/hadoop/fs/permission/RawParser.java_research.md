<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/RawParser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/RawParser.java

## Purpose
Parses raw permission modes used by `new FsPermission(String)`.

## Important APIs, Types, And Functions
The constructor uses raw symbolic and octal regexes. `getPermission()` combines parsed bits against zero and returns a short.

## Control Flow
Raw symbolic parsing accepts full nine-character permission strings with optional sticky forms, while octal parsing accepts optional sticky plus three octal digits. `getPermission` treats execute as allowed for capital-X-style combination.

## State And Persistence
Parsed mode state is inherited from `PermissionParser`.

## Dependencies And Integration Points
Used only through `FsPermission(String)`.

## Risks
Raw parsing is stricter than chmod symbolic clauses. Tests must distinguish raw full-mode strings from chmod expressions like `u+r`.

## Test Signals
Parse `rwxr-x---`, sticky variants, octal modes, invalid lengths/characters, and compare resulting shorts to expected modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/RawParser.java -->

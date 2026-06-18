<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsAction.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsAction.java

## Purpose
Models POSIX read/write/execute action sets as bit-compatible enum ordinals with symbolic strings.

## Important APIs, Types, And Functions
Values range from `NONE` to `ALL`. `implies`, `and`, `or`, `not`, and `getFsAction(String)` implement permission algebra and parsing.

## Control Flow
Permission operations use ordinal bit operations and return from a cached `values()` array. `getFsAction` linearly matches the three-character symbol.

## State And Persistence
Enum constants and `SYMBOL` strings form a stable public API. Ordinal ordering is semantically important.

## Dependencies And Integration Points
Used by `FsPermission`, ACL entries/status, permission parsers, and shell ACL display.

## Risks
Changing enum order would break bit arithmetic. `and`/`or` assume non-null operands. Symbol parsing accepts only exact canonical strings like `rw-`.

## Test Signals
Truth tables for implies/and/or/not, symbol parsing for all actions, and null handling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsAction.java -->

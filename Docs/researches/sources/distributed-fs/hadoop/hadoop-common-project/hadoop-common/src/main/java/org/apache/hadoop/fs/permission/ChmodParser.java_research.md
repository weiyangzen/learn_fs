<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ChmodParser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ChmodParser.java

## Purpose
Parses chmod-style octal or symbolic modes and applies them to an existing `FileStatus`.

## Important APIs, Types, And Functions
The constructor supplies chmod-specific regexes to `PermissionParser`. `applyNewPermission(FileStatus)` combines the parsed mode with existing permission bits.

## Control Flow
Octal modes can have an optional leading `+` and optional sticky bit. Symbolic modes allow `u/g/o/a`, `+/-/=`, `r/w/x/X/t`, comma-separated clauses, and whitespace. `applyNewPermission` enables capital `X` when the target is a directory or any execute bit is already set.

## State And Persistence
Parsed symbolic/octal mode state is inherited from `PermissionParser`; no additional fields.

## Dependencies And Integration Points
Used by chmod shell command flows. Depends on `FileStatus` and `FsPermission`.

## Risks
Regex behavior defines user-facing chmod compatibility. Incorrect `X` handling changes executable bits for files. Parser state is not reusable for multiple different mode strings.

## Test Signals
Exercise octal with and without sticky bit, symbolic add/remove/set, comma clauses, `X` on files/directories, invalid modes, and whitespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ChmodParser.java -->

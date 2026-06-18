<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionParser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionParser.java

## Purpose
Shared parser engine for chmod, umask, and raw permission strings.

## Important APIs, Types, And Functions
The constructor applies caller-provided symbolic and octal patterns. `combineModes` combines parsed sticky/user/group/other segments with existing bits. `combineModeSegments` implements `+`, `-`, `=`, and capital `X`.

## Control Flow
The parser first tries the symbolic regex, then octal regex. Symbolic parsing walks comma-separated clauses, determines affected classes, builds mode bits, records operation type per segment, and marks the parser symbolic. Octal parsing sets all segment operations to `=` and extracts optional sticky bit plus three octal digits.

## State And Persistence
Stores parsed segment modes and operation characters in protected fields for subclasses. No persistence.

## Dependencies And Integration Points
Base for `ChmodParser`, `UmaskParser`, and `RawParser`.

## Risks
Regexes are supplied by subclasses, so subtle differences define command compatibility. State fields represent only the final parsed effect per class, so malformed comma handling must be caught during parsing. `X` logic depends on caller-provided `exeOk`.

## Test Signals
Use subclass parsers to cover symbolic class defaults, comma separation, sticky bit, `+/-/=`, `X`, octal parsing, and invalid trailing input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionParser.java -->

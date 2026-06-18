# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnsupportedFileSystemException.java

## Purpose
Checked IOException used when no implementation or support exists for a requested filesystem scheme.

## Important APIs, Types, and Functions
Single message constructor; public stable exception type.

## Control Flow
No control flow; raised by filesystem lookup/initialization paths.

## State and Persistence Behavior
No persistent state beyond serialized exception fields.

## Dependencies and Integration Points
Integrated with FileSystem and AbstractFileSystem factory code and scheme resolution.

## Risks and Test Signals
Tests should cover unknown schemes and preserve message content used in diagnostics.

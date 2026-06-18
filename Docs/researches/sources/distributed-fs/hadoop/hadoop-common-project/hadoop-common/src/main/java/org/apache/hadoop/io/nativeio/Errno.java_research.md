<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/Errno.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/Errno.java

## Purpose
`Errno` is a Java enum mirror of POSIX errno categories used by Hadoop native I/O wrappers to expose native failures in a platform-neutral Java exception type.

## Important APIs and Types
The enum values include common filesystem and process errors such as `EPERM`, `ENOENT`, `EACCES`, `EEXIST`, `ENOSPC`, `ENOTEMPTY`, `EOVERFLOW`, and a fallback `UNKNOWN`.

## Control Flow
There is no runtime control flow in this file. Native code and wrapper methods select enum constants when constructing `NativeIOException`.

## State and Persistence
The enum is immutable and has no persistent state. Its ordering can matter if JNI code maps numeric errno values by ordinal, so adding or reordering values would be risky unless native mapping is name-based.

## Dependencies and Integration Points
`NativeIOException`, `NativeIO`, and callers such as secure file creation use it to detect specific conditions like `EEXIST` and translate them into Hadoop exceptions.

## Risks and Edge Cases
The list is not exhaustive for every POSIX platform. Unsupported native errno values must degrade to `UNKNOWN`, which can reduce caller-specific handling. Windows error codes do not use this enum directly except as a generic fallback.

## Test Signals
Tests should verify JNI/native mappings for representative errno values, fallback to `UNKNOWN`, and caller behavior for `EEXIST`, `ENOENT`, `EBADF`, and permission-related errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/Errno.java -->

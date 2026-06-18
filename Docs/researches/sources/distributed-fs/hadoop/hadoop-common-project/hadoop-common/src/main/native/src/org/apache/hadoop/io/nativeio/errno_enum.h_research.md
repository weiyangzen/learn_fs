<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.h

## Purpose
`errno_enum.h` declares the native errno-to-Java-enum mapping API.

## Important APIs, Types, and Functions
It declares `errno_enum_init()`, `errno_enum_deinit()`, and `errno_to_enum()`.

## Control Flow
There is no runtime flow. Callers are expected to initialize before converting errno values and deinitialize when native state is torn down.

## State and Persistence
No state is declared in the header, but the implementation owns global JNI references.

## Dependencies and Integration Points
It is included by `NativeIO.c` and participates in `NativeIOException` construction.

## Risks and Edge Cases
Callers must not invoke `errno_to_enum()` before successful initialization. The API returns a JNI object and can leave pending exceptions if Java enum lookup fails.

## Test Signals
NativeIO init and representative IOError tests validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.h -->

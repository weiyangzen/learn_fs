<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.h

## Purpose
`file_descriptor.h` declares shared JNI file descriptor conversion helpers.

## Important APIs, Types, and Functions
It declares `fd_init()`, `fd_deinit()`, and platform-specific `fd_get()`/`fd_create()` signatures using `int` on Unix and `long` on Windows.

## Control Flow
There is no runtime flow. Platform branches expose the correct native handle type to callers.

## State and Persistence
The header declares no state, but callers rely on implementation-level cached JNI refs.

## Dependencies and Integration Points
It is included by NativeIO, DomainSocket, and shared descriptor factory code.

## Risks and Edge Cases
Callers must use the platform-correct type and initialize before use. Mixing Unix and Windows assumptions would truncate handles or read the wrong Java field.

## Test Signals
Cross-platform build tests and descriptor round-trip tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.h -->

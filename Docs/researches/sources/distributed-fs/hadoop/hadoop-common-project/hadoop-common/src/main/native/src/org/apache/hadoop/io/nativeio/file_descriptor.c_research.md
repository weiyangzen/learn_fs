<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.c

## Purpose
`file_descriptor.c` provides shared JNI helpers for converting between native file descriptors/handles and `java.io.FileDescriptor` objects.

## Important APIs, Types, and Functions
Public functions are `fd_init()`, `fd_deinit()`, `fd_get()`, and `fd_create()`. Static cached values include global `FileDescriptor` class ref, the `fd` field on Unix, the `handle` field on Windows, and the no-argument constructor.

## Control Flow
`fd_init()` finds and globally references `java/io/FileDescriptor`, resolves fields and constructor, and returns early if already initialized. `fd_get()` validates non-null Java objects and reads the platform field. `fd_create()` constructs a new Java `FileDescriptor` and sets the native fd/handle field. `fd_deinit()` releases the global class reference and clears cached IDs.

## State and Persistence
Cached JNI class and field/method IDs persist process-wide between init and deinit. Returned Java `FileDescriptor` objects own only the numeric descriptor value, not the OS lifecycle by themselves.

## Dependencies and Integration Points
Many JNI files use these helpers: NativeIO, DomainSocket, SharedFileDescriptorFactory, and descriptor-passing socket code.

## Risks and Edge Cases
The cached field names depend on JDK internals (`fd`/`handle`) and can be sensitive to Java version/module access. `fd_create()` does not mark ownership semantics; Java callers must avoid double close or leaked descriptors.

## Test Signals
Tests should wrap and unwrap descriptors on Unix and Windows, validate null-object exceptions, and exercise descriptor passing and NativeIO-created descriptors across supported JDKs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.c -->

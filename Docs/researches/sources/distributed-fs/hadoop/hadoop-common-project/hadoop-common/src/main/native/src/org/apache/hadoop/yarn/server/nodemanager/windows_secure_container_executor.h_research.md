# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/yarn/server/nodemanager/windows_secure_container_executor.h

## Purpose
`windows_secure_container_executor.h` declares the JNI support API for creating and managing YARN's Windows winutils process-stub objects.

## Important APIs, types, and functions
It defines `WINUTILS_PROCESS_STUB_CLASS` as the nested Java class name and declares `winutils_process_stub_init`, `winutils_process_stub_deinit`, and `winutils_process_stub_create`. The create function accepts process, thread, and standard stream handles as `jlong`s.

## Control flow
Callers initialize cached JNI metadata, create Java stub objects from native Windows handles, and deinitialize global refs on failure or shutdown. The header itself is declarative.

## State and persistence
The header declares functions that manage process-global JNI state in the `.c` file. No state is defined directly in the header.

## Dependencies and integration points
It requires JNI types and is included by `windows_secure_container_executor.c`. It couples native code to the exact Java nested class binary name.

## Risks and test signals
Risks include class-name drift if Java nested classes are renamed, signature mismatches for the constructor, and handle type truncation on unusual platforms. Test signals include Windows native build, `initWsceNative` lookup success, and Java integration tests that instantiate the native process stub.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/CMakeLists.txt

## Purpose

This CMake file builds libhdfspp's cross-platform support object libraries. It selects the OS-specific syscall implementation and packages filesystem, syscall, and C compatibility shims for reuse by the native client and tests.

## Important APIs, types, and functions

It sets `SYSCALL_SRC` to `syscall_windows.cc` on Windows and `syscall_linux.cc` elsewhere. It creates `x_platform_obj` from `${SYSCALL_SRC}`, `utils.cc`, and `dirent.cc`. It creates `x_platform_obj_c_api` from the first object library plus `c-api/syscall.cc` and `c-api/dirent.cc`, then adds the `USE_X_PLATFORM_DIRENT` compile definition to force the C API include wrapper onto the portable dirent implementation.

## Control flow, state, and persistence

There is no runtime state. Build-time control flow is a single platform conditional that decides which syscall backend compiles. The object-library pattern avoids creating a standalone archive while allowing multiple libhdfspp binaries and tests to embed the same portability code.

## Dependencies and integration points

This file integrates with top-level native-client CMake targets and test executables that link `$<TARGET_OBJECTS:x_platform_obj>` or `$<TARGET_OBJECTS:x_platform_obj_c_api>`. The C API object target is especially important for code that expects POSIX `opendir`, `readdir`, `closedir`, and C-callable syscall wrappers.

## Risks and test signals

Risks are platform skew and duplicate symbol exposure. `x_platform_obj_c_api` intentionally includes `x_platform_obj` objects, so consumers must avoid also linking the base object target unless the build graph expects that composition. Test signals come from x-platform tests, libhdfs C API tests, Windows builds, and any test using C shims for temp files, stdout, or directory iteration.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/c-api/extern/dirent.h

## Purpose

This header wraps the core portable dirent declarations with C linkage when compiling as C++ on Windows.

## Important APIs, types, and functions

It conditionally opens `extern "C"` only when `WIN32` and `__cplusplus` are defined, includes `x-platform/c-api/core/dirent.h`, and then closes the linkage block. It does not declare additional APIs.

## Control flow, state, and persistence

There is no runtime state. Compile-time behavior decides whether `opendir`, `readdir`, and `closedir` get C linkage. Non-Windows C++ builds that force the x-platform dirent do not get the `extern "C"` wrapper from this file.

## Dependencies and integration points

This is included by `x-platform/c-api/dirent.h` when Windows or `USE_X_PLATFORM_DIRENT` is active. It prevents C++ name mangling for Windows C consumers and helps the C API object library expose predictable symbol names.

## Risks and test signals

The Windows-only linkage condition is the main compatibility detail. If non-Windows forced-wrapper C++ builds need C linkage, this header would not provide it. Link tests for C code against `x_platform_obj_c_api` and Windows CI are the relevant signals.

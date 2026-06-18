# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/c-api/dirent.h

## Purpose

This header selects either the platform `dirent.h` or libhdfspp's x-platform dirent wrapper for C consumers.

## Important APIs, types, and functions

There are no local functions. The key decision is `#if !(defined(WIN32) || defined(USE_X_PLATFORM_DIRENT))`: non-Windows builds without the forcing macro include system `<dirent.h>`, while Windows or forced builds include `x-platform/c-api/extern/dirent.h`.

## Control flow, state, and persistence

The file only controls compile-time inclusion. Runtime behavior depends on the selected implementation. With system `dirent`, semantics are native POSIX; with x-platform dirent, behavior is the reduced compatibility layer backed by C++ filesystem.

## Dependencies and integration points

It integrates C code with the `x-platform` object library. `x_platform_obj_c_api` defines `USE_X_PLATFORM_DIRENT`, so that target consistently uses the wrapper even where a system header exists. Tests and libhdfs C compatibility sources include this header to avoid platform-specific conditionals.

## Risks and test signals

The main risk is inconsistent ABI or symbol choice if one translation unit includes system `dirent.h` while another expects the x-platform functions. Cross-platform CI and tests that compile both C and C++ consumers with `USE_X_PLATFORM_DIRENT` catch selector drift.

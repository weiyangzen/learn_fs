# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/c-api/dirent.cc

## Purpose

This file implements the C `opendir`, `readdir`, and `closedir` compatibility layer on top of `XPlatform::Dirent`.

## Important APIs, types, and functions

`opendir(const char *)` allocates a `DIR` and stores a newly allocated `XPlatform::Dirent`. `readdir(DIR *)` calls `NextFile()`, maps `std::monostate` to end-of-directory, maps `std::error_code` to `errno`, and copies the current filename into a static `struct dirent`. `closedir(DIR *)` deletes the C++ iterator and the wrapper.

## Control flow, state, and persistence

Each opened directory has heap-owned iteration state. `readdir()` uses one static `dirent` buffer, matching common POSIX behavior where returned storage is overwritten by subsequent calls, but making concurrent `readdir()` callers share state. It zeroes the `d_name` buffer before copying the filename and returns `nullptr` on end or error.

## Dependencies and integration points

The implementation depends on C++17 filesystem, variants, `errno`, and the selector header `x-platform/c-api/dirent.h`. It is built into `x_platform_obj_c_api` and can replace system `dirent` for Windows or forced-portable builds. Legacy C tests and tools can include the wrapper without knowing about C++ filesystem.

## Risks and test signals

Risks include uncaught exceptions from constructing `XPlatform::Dirent`, static return storage not being thread-safe, `errno = 1` for long filenames instead of a precise platform code, and leaked memory if callers skip `closedir()`. Test signals are directory iteration through all entries, error propagation for invalid paths, long filename failures, and C ABI linkage on Windows.

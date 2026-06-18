# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/c-api/core/dirent.h

## Purpose

This header defines the portable C surface that emulates a small POSIX `dirent` API for platforms or build modes that cannot use system `<dirent.h>`.

## Important APIs, types, and functions

It defines a C-compatible `DIR` struct holding `void *x_platform_dirent_ptr`, a minimal `struct dirent` with fixed `char d_name[256]`, and prototypes for `opendir()`, `readdir()`, and `closedir()`. The `void *` indirection lets C code hold an opaque pointer to the C++ `XPlatform::Dirent` implementation.

## Control flow, state, and persistence

The header itself has no control flow. Runtime state is owned by the implementation in `c-api/dirent.cc`: `opendir()` allocates a `DIR` plus `XPlatform::Dirent`, `readdir()` advances iteration, and `closedir()` releases both. Directory iteration state is per `DIR`; returned `dirent` content is static in the implementation.

## Dependencies and integration points

This file is included through `x-platform/c-api/extern/dirent.h` and the higher-level `x-platform/c-api/dirent.h` selector. It exists to support C code and legacy libhdfs-compatible tests on Windows or when `USE_X_PLATFORM_DIRENT` is defined.

## Risks and test signals

The fixed 256-byte `d_name` cap differs from some native platforms and can fail long filenames. The API is intentionally narrow and does not expose inode, type, or `errno` parity beyond what the implementation sets. Directory traversal tests on Windows and long-name error cases are the best signals.

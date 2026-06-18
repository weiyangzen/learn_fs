# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/config.h.cmake

## Purpose
CMake template for generated native configuration header.

## Important APIs, Types, And Functions
Defines include guard `CONFIG_H` and exposes `_FUSE_DFS_VERSION`, `HAVE_BETTER_TLS`, and `HAVE_INTEL_SSE_INTRINSICS` through `#cmakedefine`.

## Control Flow
Processed by `configure_file` in `src/CMakeLists.txt`; no runtime control flow.

## State, Persistence, And Dependencies
Persists build-time feature probes into `config.h` under the binary directory. Values depend on compiler checks and `_FUSE_DFS_VERSION`.

## Integration Points
Included by `fuse_dfs.h` and other native code needing build feature macros.

## Risks
Incorrect CMake probe values can compile code paths unsupported by the compiler or hide optimized features. The generated header must be in include directories for native targets.

## Test Signals
Build failures around undefined version or feature macros indicate configuration/header include path issues.

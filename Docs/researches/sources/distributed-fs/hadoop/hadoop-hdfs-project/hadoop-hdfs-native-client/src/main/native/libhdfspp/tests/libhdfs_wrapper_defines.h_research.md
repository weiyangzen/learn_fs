# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/libhdfs_wrapper_defines.h

## Purpose

This header defines macros that rename legacy libhdfs public symbols for side-by-side test linking.

## Important APIs, types, and functions

It maps many functions, enums, structs, and typedefs to `libhdfs_`-prefixed names, including connection/builder APIs, file operations, metadata operations, zero-copy read APIs, hedged-read metrics, stream builder APIs, `hdfsFS`, `hdfsFile`, `hdfsFileInfo`, and object-kind constants.

## Control flow, state, and persistence

There is no runtime logic. The file changes token names before including libhdfs headers or source. State and behavior come from the renamed included implementation.

## Dependencies and integration points

It is paired with `libhdfs_wrapper_undefs.h` and used by `libhdfs_wrapper.c` / `libhdfs_wrapper.h`. The wrapper target relies on the macro list to avoid duplicate symbols when libhdfspp is linked into the same process.

## Risks and test signals

The macro list must track the libhdfs ABI. One visible risk is typo-level mistakes in renamed constants, which can silently create inconsistent names. Compile/link failures and missing wrapper declarations indicate drift; side-by-side integration tests validate practical coverage.

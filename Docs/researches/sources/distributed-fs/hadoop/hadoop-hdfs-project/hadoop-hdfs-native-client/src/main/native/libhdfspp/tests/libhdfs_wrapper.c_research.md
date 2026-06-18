# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/libhdfs_wrapper.c

## Purpose

This wrapper compiles the legacy `libhdfs/hdfs.c` implementation under renamed symbols so tests can link it beside libhdfspp without collisions.

## Important APIs, types, and functions

The file includes `libhdfs_wrapper_defines.h`, then includes the production C source `libhdfs/hdfs.c`, then includes `libhdfs_wrapper_undefs.h`. The macros rename libhdfs functions and structs with a `libhdfs_` prefix.

## Control flow, state, and persistence

There is no local runtime logic. The included libhdfs source provides all behavior under renamed symbols. Runtime state is whatever libhdfs normally maintains for JVM, filesystem, file handles, and errors.

## Dependencies and integration points

It is built into `hdfspp_test_shim_static` for comparison or shim tests that need both libhdfs and libhdfspp APIs in one binary. It relies on macro hygiene from the defines/undefs headers.

## Risks and test signals

Including a `.c` source directly is fragile but effective for symbol rewriting. Risks include missed symbol macros, macro leakage, and source changes adding new symbols not renamed. Link failures or duplicate symbol errors are the main signals.

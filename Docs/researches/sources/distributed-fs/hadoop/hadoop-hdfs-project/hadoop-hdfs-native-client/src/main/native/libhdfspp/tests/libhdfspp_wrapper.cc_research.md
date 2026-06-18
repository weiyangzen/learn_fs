# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/libhdfspp_wrapper.cc

## Purpose

This wrapper compiles the libhdfspp C binding implementation under renamed symbols for side-by-side test linking.

## Important APIs, types, and functions

It includes `libhdfspp_wrapper_defines.h`, then includes `bindings/c/hdfs.cc`, then includes `libhdfs_wrapper_undefs.h`. The macros rename libhdfspp C API symbols with a `libhdfspp_` prefix.

## Control flow, state, and persistence

There is no local runtime logic. The included C++ binding source provides behavior under renamed symbols. State is the normal libhdfspp C binding state: builders, filesystem handles, file handles, async futures, errors, and callbacks.

## Dependencies and integration points

The file is part of the test shim/static integration setup. It lets tests compare or combine legacy libhdfs and libhdfspp APIs without duplicate exported names.

## Risks and test signals

The include of `libhdfs_wrapper_undefs.h` rather than a libhdfspp-specific undefs header relies on shared macro names and may be intentional but deserves attention. Risks include missed symbols when the C binding grows. Link and wrapper tests catch most drift.

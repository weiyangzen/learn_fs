# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/hdfs_shim.c

## Purpose

This C file provides a lightweight libhdfs-compatible shim for integration tests where libhdfspp is not yet feature-complete or where tests need controlled placeholder behavior.

## Important APIs, types, and functions

It defines internal `hdfs_internal`, `hdfsFile_internal`, and `hdfsBuilder` structs plus many libhdfs symbols: connect/builder functions, config accessors, file open/read/write/future APIs, filesystem metadata APIs, zero-copy read helpers, hedged metrics helpers, and extended operations such as `hdfsFind()`. A `REPORT_FUNCTION_NOT_IMPLEMENTED` macro centralizes stderr reporting and errno-style failure for unsupported calls.

## Control flow, state, and persistence

Implemented paths allocate simple handles, copy builder strings, return placeholder success/failure values, and in selected functions delegate or emulate enough behavior for test linkage. Unsupported functions report the current function name and return error values. State is heap-allocated test handles and simple strings; no real HDFS state persists through this shim unless delegated elsewhere.

## Dependencies and integration points

The shim includes libhdfs headers and is built into `hdfspp_test_shim_static` with wrapper sources under the `HADOOP_BUILD` integration-test branch. It lets existing libhdfs tests link while libhdfspp covers a subset of behavior.

## Risks and test signals

Because many functions are placeholders, this shim can mask missing production functionality if tests accept stubbed behavior. Its value is compatibility and link coverage, not full correctness. Test failures around unimplemented reports indicate integration tests have reached an unsupported libhdfs surface.

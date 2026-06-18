# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/hdfspp_errors.cc

## Purpose

This unit test validates libhdfspp C API error reporting for invalid filesystem/file handles and last-error buffer sizing.

## Important APIs, types, and functions

Tests call `hdfsRead()` and `hdfsGetLastError()` from `<hdfs/hdfs.h>` and `<hdfspp/hdfs_ext.h>`. Cases are `NullFileSystem`, `NullFileHandle`, `ZeroLength`, `NegativeLength`, and `MessageTruncation`.

## Control flow, state, and persistence

Each test triggers an invalid `hdfsRead()` call, expects `-1`, then asks for the last error with different buffer lengths. Zero or negative output lengths should leave the buffer unchanged/empty, while a length of 10 should return a truncated prefix. Last-error state is process-local C API state.

## Dependencies and integration points

The file depends on libhdfs and libhdfspp C headers, protobuf cleanup, gmock, and C string handling. It protects error paths in the C bindings used by applications that cannot consume C++ `Status`.

## Risks and test signals

The exact expected messages are part of the user-facing C ABI contract. Risks include thread-local versus global last-error behavior, truncation off-by-one errors, and crashes when handles are null. This test provides focused coverage of invalid-argument robustness.

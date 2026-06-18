# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/libhdfspp_wrapper_defines.h

## Purpose

This header defines macros that rename libhdfspp C API symbols for side-by-side testing with libhdfs.

## Important APIs, types, and functions

It maps core libhdfs-compatible APIs and libhdfspp extensions to `libhdfspp_`-prefixed names. In addition to common connection, file, builder, metadata, and metrics symbols, it covers libhdfspp-specific APIs such as `hdfsGetLastError`, `hdfsCancel`, block locations, find, and snapshot operations.

## Control flow, state, and persistence

There is no runtime behavior. The preprocessor replaces public names before including libhdfspp C binding declarations or implementation.

## Dependencies and integration points

It is used by `libhdfspp_wrapper.cc` and `libhdfspp_wrapper.h` and is part of the integration-test shim strategy. It must align with libhdfspp's C ABI and with undef cleanup.

## Risks and test signals

The macro set must be updated whenever the C binding exports new names. Otherwise tests may collide with real symbols or omit coverage. Build/link failures are the most immediate signal; broader integration tests validate that renamed APIs still behave correctly.

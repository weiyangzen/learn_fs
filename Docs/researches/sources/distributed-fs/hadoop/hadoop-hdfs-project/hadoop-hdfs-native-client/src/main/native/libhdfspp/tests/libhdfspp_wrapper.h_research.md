# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/libhdfspp_wrapper.h

## Purpose

This header exposes renamed libhdfspp C binding declarations to tests.

## Important APIs, types, and functions

It wraps inclusion of the libhdfspp C headers with `libhdfspp_wrapper_defines.h` and the corresponding undef cleanup, making APIs available as `libhdfspp_*` symbols.

## Control flow, state, and persistence

The file has no runtime behavior. It is a compile-time symbol rewriting aid.

## Dependencies and integration points

It pairs with `libhdfspp_wrapper.cc` and the libhdfspp defines header. Tests use it when both libhdfs and libhdfspp need to be visible in one process.

## Risks and test signals

As with the C source wrapper, the risk is macro drift when the C binding adds APIs. Compile failures, duplicate symbols, or missing declarations in side-by-side tests are the main signals.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/libhdfs_wrapper_undefs.h

## Purpose

This header undefines the legacy libhdfs renaming macros after a wrapper include.

## Important APIs, types, and functions

It contains `#undef` entries corresponding to `libhdfs_wrapper_defines.h`, covering connection, builder, file, metadata, zero-copy, metrics, stream, type, and enum symbols.

## Control flow, state, and persistence

There is no runtime behavior. It restores preprocessor hygiene so later includes in the same translation unit are not accidentally renamed.

## Dependencies and integration points

It is included after `libhdfs/hdfs.c` or libhdfs headers in wrapper translation units. It should remain a mirror of the defines header.

## Risks and test signals

If an undef is missing, macro leakage can corrupt unrelated code. If an undef exists without a matching define it is harmless, but drift makes maintenance harder. Compiling mixed libhdfs/libhdfspp tests is the main signal.

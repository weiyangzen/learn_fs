# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/libhdfs_wrapper.h

## Purpose

This header exposes the renamed legacy libhdfs declarations to tests.

## Important APIs, types, and functions

It wraps inclusion of the normal libhdfs header with `libhdfs_wrapper_defines.h` and `libhdfs_wrapper_undefs.h`, so declarations such as `hdfsConnect`, `hdfsRead`, and related types are visible as `libhdfs_*` names.

## Control flow, state, and persistence

The header has no runtime behavior. It only rewrites declarations at preprocessing time.

## Dependencies and integration points

It depends on the defines/undefs macro sets and the upstream libhdfs public header. Tests use it when they need to call legacy libhdfs and libhdfspp in the same translation unit.

## Risks and test signals

The header must stay synchronized with the macro lists. If libhdfs adds public APIs not covered by the defines header, tests may collide with libhdfspp symbols or fail to compile. The wrapper build is the primary signal.

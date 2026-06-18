# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/hdfs_builder_test.cc

## Purpose

This test validates the C extension builder APIs for creating a builder from a configuration directory and reading or setting builder configuration values.

## Important APIs, types, and functions

It tests `hdfsNewBuilderFromDirectory()`, `hdfsFreeBuilder()`, `hdfsBuilderConfGetStr()`, `hdfsConfStrFree()`, `hdfsBuilderConfGetInt()`, and `hdfsBuilderConfSetStr()`. It uses `writeSimpleConfig()` and temporary directories/files.

## Control flow, state, and persistence

`TestStubBuilder` ensures builders can be allocated from existing and missing directories and freed. `TestRead` creates `core-site.xml`, reads string and int config values, and verifies missing keys return success with null/default outputs. `TestSet` creates an empty builder from a nonexistent directory, sets values, reads them as ints, and verifies overwrite behavior.

## Dependencies and integration points

The file includes `hdfspp/hdfs_ext.h`, configuration test helpers, temp utilities, gmock, and protobuf shutdown. It tests the C-facing builder behavior that wraps `ConfigurationLoader` and `HdfsConfiguration`.

## Risks and test signals

Risks are memory ownership for returned strings, missing-directory semantics, and overlay/overwrite consistency. The test's explicit `hdfsConfStrFree()` call is an ownership signal for C API users. It does not connect to a cluster; it is focused on builder-local state.

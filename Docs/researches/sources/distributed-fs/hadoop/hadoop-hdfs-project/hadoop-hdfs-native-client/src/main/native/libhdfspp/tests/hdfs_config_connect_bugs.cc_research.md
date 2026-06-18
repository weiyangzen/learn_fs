# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/hdfs_config_connect_bugs.cc

## Purpose

This regression test covers HDFS-11294: connecting to an HA nameservice with unresolvable endpoints should fail cleanly rather than crash.

## Important APIs, types, and functions

The test defines static `core-site.xml` and `hdfs-site.xml` text for a nameservice with two bogus NameNode hostnames. It uses `hdfsNewBuilderFromDirectory()`, `hdfsBuilderSetNameNode()`, `hdfsBuilderConnect()`, and `hdfsGetLastError()`.

## Control flow, state, and persistence

The test writes temporary config files, creates a builder pointing to that directory, sets the NameNode to `NAMESERVICE1`, attempts to connect, and expects a null `hdfsFS`. It then reads the last error and expects `"Exception:No endpoints found for namenode"`. Temporary config files are removed explicitly.

## Dependencies and integration points

It depends on `hdfspp/hdfs_ext.h`, configuration helpers, protobuf shutdown, C file I/O, and `TestUtils::TempDir`. It validates HA configuration parsing, endpoint resolution, and RPC engine error reporting through the C API.

## Risks and test signals

The important signal is "no crash" when DNS resolution yields no usable endpoints. The expected error string is brittle but protects user-facing diagnostics. The malformed `ipc.client.connect.retry.interval` property in the fixture also exercises parser tolerance around incomplete property syntax.

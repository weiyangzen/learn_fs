# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/hdfs_test.h

## Purpose
`hdfs_test.h` is a private test-only header for libhdfs internals. It exposes a narrow set of functions from `libhdfs/hdfs.c` that are intentionally not part of the normal exported API but are needed by native tests to force and inspect direct-read behavior and domain socket security.

## Important APIs and types
The file forward-declares `struct hdfsFile_internal`, matching the private `hdfsFile` implementation in `hdfs.c`. It declares `hdfsFileUsesDirectRead`, `hdfsFileDisableDirectRead`, `hdfsFileUsesDirectPread`, `hdfsFileDisableDirectPread`, and `hdfsDisableDomainSocketSecurity`.

## Control flow and integration
Tests include this header to verify capability detection after `hdfsOpenFile` or async open creates an input stream. The disable functions mutate the `flags` field inside `hdfsFile_internal` so tests can drive the fallback Java byte-array read paths after first exercising the direct `ByteBuffer` paths.

## State and persistence
The header itself has no persistent state. It exposes mutators for per-file in-memory capability bits and a process/JVM-level helper that disables Hadoop domain socket bind-path validation for short-circuit read tests.

## Dependencies
It depends only on the private shape of libhdfs, specifically the existence of `struct hdfsFile_internal` and the corresponding implementations in `hdfs.c`. It is guarded for C++ callers with `extern "C"`.

## Risks
Because this is a test-only header, accidentally installing or treating it as a public ABI would expose private internals and allow callers to corrupt stream capability state. Tests using the disable functions must keep direct-read and direct-pread semantics separate; `test_libhdfs_ops.c` explicitly checks that disabling one flag does not disable the other.

## Test signals
`test_libhdfs_ops.c` uses this header to validate direct read and direct pread capability detection and fallback. Zero-copy and stress tests indirectly rely on the same short-circuit/domain-socket support but use public zero-copy APIs rather than these test hooks.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/bad_datanode_test.cc

## Purpose

This unit test validates how `FileHandleImpl` handles bad datanodes, datanode exclusion, and file event callbacks during read attempts.

## Important APIs, types, and functions

The file defines `MockReader`, `MockDNConnection`, and `PartialMockFileHandle`. `PartialMockFileHandle` overrides `CreateBlockReader()` and `CreateDataNodeConnection()` to inject mocks. Tests are `TestNoNodes`, `NNEventCallback`, `RecoverableError`, and `InternalError`.

## Control flow, state, and persistence

Each test constructs synthetic `FileInfo` and `LocatedBlockProto` data with datanode IDs, then calls `AsyncPreadSome()`. `TestNoNodes` pre-marks the only datanode as bad and expects a resource-unavailable status with zero bytes. `NNEventCallback` verifies connect and read event callbacks and forces an event-supplied failure. The error tests check `FileHandle::ShouldExclude()` decisions for resource-unavailable versus internal exception statuses.

## Dependencies and integration points

The test integrates `reader/block_reader.h`, `fs/filehandle.h`, libhdfs event callbacks, bad datanode tracking, protobuf block metadata, Boost.Asio buffers, and gmock invocation helpers. It is linked through the test CMake target with reader, fs, RPC, and common libraries.

## Risks and test signals

The test is a strong signal for avoiding over-aggressive datanode exclusion: transient resource unavailable errors should not blacklist a datanode, while internal server exceptions should. It also protects event callback ordering. Risks are brittle synthetic block construction and assumptions that async callbacks complete synchronously with the mocks.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-allow-snapshot-mock.h

## Purpose

This header declares the gmock test double for the `hdfs allowSnapshot` tool.

## Important APIs, types, and functions

`AllowSnapshotMock` derives from `hdfs::tools::AllowSnapshot`, deletes copy/move operations, overrides the destructor, declares `SetExpectations()`, and mocks `HandleHelp()` and `HandlePath(const std::string&)`.

## Control flow, state, and persistence

The class constructor forwards `argc` and `argv` to the production `AllowSnapshot` base class. Test control flow is established by `SetExpectations()` in the `.cc` file and by gmock method calls. There is no persistent state beyond base parser state and gmock expectations.

## Dependencies and integration points

It depends on gmock and the production `hdfs-allow-snapshot.h` tool header. It is used by the aggregate tool test suite to validate command-line parsing without performing real HDFS snapshot operations.

## Risks and test signals

The mock only covers help and single-path handling, matching the expected surface of allowSnapshot. If the production tool gains more modes or validation paths, this mock and shared tool test cases need updates. Passing tests confirm parser-to-handler dispatch, not NameNode behavior.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/protobuf.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/protobuf.h

## Purpose
Provides continuation stages for reading and writing length-delimited protobuf messages over Asio streams.

## Important APIs, Types, And Functions
`ReadDelimitedPBMessageContinuation<Stream, MaxMessageSize>` reads a varint length plus message into a fixed array, then merges into a `MessageLite`. `WriteDelimitedPBMessageContinuation<Stream>` serializes a delimited protobuf with `SerializeDelimitedProtobufMessage` and writes it. Factory helpers return heap-allocated continuation stages.

## Control Flow
The read stage uses `boost::asio::async_read` with a custom completion condition that keeps requesting bytes until the varint length and payload are present. The write stage serializes first, fails immediately on serialization error, otherwise async-writes the buffer and forwards status.

## State And Persistence
Read state includes the shared stream, destination message pointer, and fixed buffer. Write state includes the shared stream, source message pointer, and serialized string buffer. No persistent state exists.

## Dependencies And Integration Points
Depends on Boost.Asio, protobuf lite, coded streams, and `common/util.h`. It is used by wire-protocol components that exchange protobuf headers/messages.

## Risks
Read parsing uses `assert` for varint/message success and message-size bounds, which disappears in release builds. The default max read buffer is only 512 bytes, so larger messages need explicit template sizing. The write factory takes a non-const message pointer even though the continuation stores a const pointer.

## Test Signals
Tests should read/write normal messages, messages near and above `MaxMessageSize`, malformed varints, serialization failures, async stream errors, and release-mode behavior when assertions are compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/protobuf.h -->

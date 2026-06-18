<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.cc

## Purpose
Implements `DataNodeConnectionImpl`, the socket-backed `AsyncStream` used by block readers to connect to and communicate with one HDFS DataNode.

## Important APIs, Types, And Functions
The constructor builds a TCP socket from an `IoService`, extracts DataNode transfer endpoint and UUID from `DatanodeInfoProto`, and optionally copies a block token. `Connect` starts `boost::asio::async_connect`. `Cancel` safely disconnects the socket. `async_read_some` and `async_write_some` emit event callbacks and forward to the socket.

## Control Flow
Callers construct the connection, call `Connect`, and receive a status plus shared connection in the handler. Read/write operations lock briefly around posting socket async operations. Cancellation closes the socket so pending operations should complete with errors.

## State And Persistence
State includes the socket, one endpoint, copied token, UUID, event handler pointer, and a mutex. It is per-connection and in-memory.

## Dependencies And Integration Points
Depends on Boost.Asio, generated HDFS protobufs, `IoService`, `AsyncStream`, `LibhdfsEvents`, logging, and `SafeDisconnect`. Created by `FileHandleImpl` for block reads and consumed by `BlockReaderImpl`.

## Risks
The endpoint is built from `ipaddr()` with `address::from_string`, so hostnames or invalid IP strings throw during construction. Event handler pointer is raw and must outlive the connection. The derived class declares its own `uuid_`, hiding the base member of the same name; callers through a base pointer may observe the base value instead of the derived value. Async read/write serialization is minimal and does not make simultaneous operations fully safe.

## Test Signals
Tests should cover successful and failed connect, invalid IP input, token copy, cancellation during connect/read/write, event emission counts, base-pointer UUID visibility, and ASAN lifetime checks for event handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.h

## Purpose
Declares the abstract DataNode connection stream and the concrete socket-backed implementation used by HDFS block readers.

## Important APIs, Types, And Functions
`DataNodeConnection` derives from `AsyncStream`, stores public UUID/token members, and declares `Connect` and `Cancel`. `SocketDeleter` safely disconnects sockets before deletion. `DataNodeConnectionImpl` owns a unique TCP socket, one endpoint, event handler pointer, state mutex, and overrides connect/read/write/cancel.

## Control Flow
Implementation creates sockets and forwards async I/O in `datanodeconnection.cc`.

## State And Persistence
Per-object socket, endpoint, token, UUID, and callback pointer state is in-memory. No durable state exists.

## Dependencies And Integration Points
Included by `FileHandleImpl`, block reader code, and tests/mocks. It depends on protobuf, `IoService`, `AsyncStream`, events, logging, utilities, and debug allocation helpers.

## Risks
The public base data members and duplicate derived `uuid_` make object state easy to misuse. Raw event handler ownership is not expressed in the type. Since it derives from `enable_shared_from_this`, `Connect` must only be called on shared-owned instances.

## Test Signals
Compile tests should mock `DataNodeConnection`; runtime tests should instantiate through `make_shared`, call `Connect`, and validate destructor/socket cleanup under cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.h -->

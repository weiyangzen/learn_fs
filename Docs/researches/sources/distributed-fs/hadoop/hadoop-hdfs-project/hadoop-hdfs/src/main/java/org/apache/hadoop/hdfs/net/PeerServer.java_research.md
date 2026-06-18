# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/PeerServer.java

Purpose: Defines the common server-side abstraction for accepting HDFS data-transfer peers, independent of whether the underlying transport is TCP or Unix domain sockets.

Important APIs and functions: `setReceiveBufferSize(int)`, `getReceiveBufferSize()`, `accept()`, `getListeningString()`, and `close()` form the contract implemented by `TcpPeerServer` and `DomainPeerServer`.

Control flow: This interface has no implementation logic. Implementations block in `accept()` until a connection arrives or a configured timeout/error occurs.

State and persistence behavior: No state in the interface. Implementations own sockets or other listening resources and must free them in `close()`.

Dependencies and integration points: Extends `Closeable` and uses `Peer`, `IOException`, and `SocketTimeoutException`. DataNode server code can work against this transport-neutral interface.

Risks: Implementations must keep buffer-size semantics and close behavior consistent. Callers must be prepared for `SocketTimeoutException` separately from other IO failures.

Test signals: Interface-level tests are integration tests that run the same accept/buffer/close expectations against TCP and domain socket implementations.

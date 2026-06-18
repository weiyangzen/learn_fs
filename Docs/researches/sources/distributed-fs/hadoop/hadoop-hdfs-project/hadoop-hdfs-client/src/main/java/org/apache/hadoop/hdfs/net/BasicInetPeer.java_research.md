# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/BasicInetPeer.java

## Purpose
`BasicInetPeer` adapts a regular Java `Socket` without an associated channel to the HDFS `Peer` interface.

## Important APIs, types, and functions
The constructor captures the socket, its input/output streams, and whether the socket address is local. `getInputStreamChannel()` returns null because the socket has no channel. Read timeout, receive buffer, TCP_NODELAY, close, address string, stream, locality, domain socket, and security methods implement `Peer`.

## Control flow
Operations mostly delegate to the underlying socket and cached streams. `setWriteTimeout` is intentionally a no-op because blocking Java socket writes cannot have a timeout without NIO.

## State and persistence behavior
State is the socket, cached streams, and local flag. Closing closes the socket. No persistence occurs.

## Dependencies and integration points
It depends on `Socket` and `DomainSocket` types and implements `Peer` for DataNode data-transfer clients that cannot use NIO channels.

## Risks and test signals
Tests should cover null channel behavior, no-op write timeout, address-string behavior before/after connection, local detection, stream reuse, close idempotence, and `hasSecureChannel=false`. Callers needing write timeouts should use `NioInetPeer`.

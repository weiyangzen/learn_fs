# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/Peer.java

## Purpose
`Peer` is the HDFS client abstraction for a DataNode connection, hiding whether the transport is a regular socket, NIO socket, UNIX domain socket, or encrypted wrapper.

## Important APIs, types, and functions
The interface exposes input channel, read/write timeout setters, receive buffer size, TCP_NODELAY, close state, close, remote/local address strings, input/output streams, locality, optional `DomainSocket`, and `hasSecureChannel`.

## Control flow
As an interface it has no executable flow. Implementations define how timeout, close, and stream semantics are realized for each transport.

## State and persistence behavior
No state exists in the interface. Implementations own transport resources.

## Dependencies and integration points
It extends `Closeable` and references Java stream/channel types plus Hadoop `DomainSocket`. `BlockReaderRemote`, peer caches, data-transfer encryption, and domain-socket short-circuit paths depend on this abstraction.

## Risks and test signals
Interface-level tests should verify all implementations satisfy close idempotence, stream lifetime until peer close, timeout behavior documented for basic sockets, locality/security flags, and optional channel/domain socket nullability. Callers must handle a null input channel for `BasicInetPeer`.

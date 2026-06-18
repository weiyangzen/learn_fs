# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/DomainPeer.java

## Purpose
`DomainPeer` adapts a UNIX domain socket to the HDFS `Peer` interface for local DataNode communication.

## Important APIs, types, and functions
The constructor stores the `DomainSocket`, streams, and channel. Read/write timeout and receive buffer methods use domain-socket attributes. Address methods return `unix:<path>` and `<local>`. `isLocal()` always returns true, `getTcpNoDelay()` returns false, `getDomainSocket()` returns the underlying socket, and `hasSecureChannel()` returns true.

## Control flow
All I/O properties delegate to the domain socket. `close` closes the domain socket. Security is treated as local secure communication based on domain socket path permission controls.

## State and persistence behavior
State is the domain socket and cached stream/channel handles. No persistence occurs.

## Dependencies and integration points
It depends on Hadoop `DomainSocket` and implements `Peer` for local short-circuit/domain-socket data paths and peer caches.

## Risks and test signals
Tests should cover timeout attributes, receive buffer attribute, close/open status, path-based address strings, local/secure flags, and channel availability. Security assumptions depend on correct domain socket path permission validation outside this class.

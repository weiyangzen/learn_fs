# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/NioInetPeer.java

## Purpose
`NioInetPeer` adapts a socket with a channel to `Peer` using Hadoop `SocketInputStream` and `SocketOutputStream`, enabling simulated blocking I/O with read and write timeouts.

## Important APIs, types, and functions
The constructor creates NIO-backed socket streams from the socket channel and records locality. `getInputStreamChannel()` returns the input stream because it is a `ReadableByteChannel`. Timeout methods set timeouts on the Hadoop socket streams. Other methods expose buffer, TCP_NODELAY, addresses, streams, locality, null domain socket, insecure channel, and close behavior.

## Control flow
Close closes the input stream and then the output stream in a finally block; closing either stream also closes the socket. Reads/writes happen through the wrapped Hadoop streams.

## State and persistence behavior
State is the socket, NIO-backed streams, and local flag. No persistence occurs.

## Dependencies and integration points
It depends on Hadoop `SocketInputStream`, `SocketOutputStream`, `Peer`, and Java sockets. It is the preferred TCP peer when timeout-capable writes and channel-based packet reads are needed.

## Risks and test signals
Tests should cover timeout updates, channel availability, close behavior when input close fails, address strings, local detection, and `hasSecureChannel=false`. The constructor requires a socket channel; callers must not pass a socket without one.

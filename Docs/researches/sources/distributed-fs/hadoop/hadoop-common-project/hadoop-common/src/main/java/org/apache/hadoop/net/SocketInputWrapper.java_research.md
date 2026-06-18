# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketInputWrapper.java

Purpose: filter stream wrapper that gives callers a consistent read-timeout API whether a socket has an NIO channel or only classic blocking streams.

Important APIs/types/functions: package-private constructor, `setTimeout`, and `getReadableByteChannel`.

Control flow: construction records whether `Socket.getChannel()` is present and asserts that channel-backed sockets use a `SocketInputStream`. `setTimeout` delegates to `SocketInputStream.setTimeout` for channel sockets or to `Socket.setSoTimeout` for non-channel sockets. `getReadableByteChannel` is allowed only for channel-backed sockets.

State and persistence: holds the socket, wrapped input stream, and `hasChannel` flag; no persistence.

Dependencies and integration: used by socket utility code that must support both NIO and classic sockets.

Risks: for non-channel sockets, timeout changes affect all readers of that socket, not only this wrapper. Long timeout values are cast to `int` in the non-channel path. Creating multiple wrappers on one socket can produce inconsistent timeout expectations.

Test signals: covered indirectly by socket utility and timeout tests.

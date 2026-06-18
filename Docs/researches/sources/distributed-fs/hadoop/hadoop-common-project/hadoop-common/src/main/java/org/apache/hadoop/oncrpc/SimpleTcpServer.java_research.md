# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpServer.java

Purpose: small Netty TCP server wrapper for ONC RPC programs.

Important APIs/types/functions: constructor, `run`, `getBoundPort`, and `shutdown`.

Control flow: `run` creates boss and worker event loop groups, configures `ServerBootstrap`, installs pipeline stages for RPC frame decoding, message parsing, RPC program handling, and TCP response framing, binds the requested port, and stores the actual bound port. `shutdown` closes the server channel and shuts down both groups.

State and persistence: stores configured and bound port, handler, channel, event loop groups, and worker count; no persistence.

Dependencies and integration: used to host `RpcProgram` implementations. Depends on `RpcUtil` stages and Netty server channels.

Risks: class comment says UDP server though implementation is TCP. Worker group uses `Executors.newCachedThreadPool`, so sizing must be controlled by Netty worker count. `shutdownGracefully` is not awaited.

Test signals: simple server and portmap/NFS-related integration tests cover binding and shutdown.

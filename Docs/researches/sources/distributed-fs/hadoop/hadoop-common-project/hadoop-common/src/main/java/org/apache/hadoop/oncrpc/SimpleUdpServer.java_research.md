# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleUdpServer.java

Purpose: small Netty UDP server wrapper for ONC RPC handlers.

Important APIs/types/functions: constructor, `run`, `getBoundPort`, and `shutdown`.

Control flow: `run` creates a worker event loop group, configures a `Bootstrap` with `NioDatagramChannel`, buffer sizes, broadcast and reuse options, installs parser/program/UDP-response stages, binds the port, and records the actual bound port. `shutdown` closes the channel and group.

State and persistence: stores configured port, handler, worker count, bound port, bootstrap, channel, and worker group; no persistence.

Dependencies and integration: used for UDP RPC services and portmap-like handlers. Depends on `RpcUtil` stages and Netty datagram channels.

Risks: response stage assumes `InetSocketAddress` recipients. `shutdownGracefully` is not awaited. Broadcast is enabled for all uses, which may be broader than needed.

Test signals: portmap and simple UDP integration tests cover binding, request parsing, response sending, and shutdown.

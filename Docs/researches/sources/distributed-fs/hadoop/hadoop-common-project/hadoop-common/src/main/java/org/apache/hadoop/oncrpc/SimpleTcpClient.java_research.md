# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpClient.java

Purpose: minimal Netty TCP client that connects to an RPC server and sends one XDR request.

Important APIs/types/functions: constructors, `setChannelHandler`, `run`, and `stop`.

Control flow: `run` creates a `NioEventLoopGroup`, configures `Bootstrap` with `NioSocketChannel`, installs frame decoder and `SimpleTcpClientHandler`, connects synchronously, and if `oneShot` waits for close and shuts down. `stop` waits on `closeFuture` then shuts down the worker group.

State and persistence: stores host, port, request, one-shot flag, worker group, and connection future; no persistence.

Dependencies and integration: base for `RegistrationClient`; used in tests and simple RPC flows.

Risks: interrupted exceptions are printed to stderr rather than logged or propagated. If `run` fails before creating `workerGroup`, `stop` may null-dereference in unusual paths. Long-lived non-one-shot users must call `stop`.

Test signals: integration tests cover simple client/server request flow and registration subclass behavior.

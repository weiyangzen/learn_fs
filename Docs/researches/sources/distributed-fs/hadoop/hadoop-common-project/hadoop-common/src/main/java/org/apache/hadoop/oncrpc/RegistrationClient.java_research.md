# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RegistrationClient.java

Purpose: TCP client specialization for registering or unregistering an RPC program with portmap/rpcbind and validating the reply.

Important APIs/types/functions: constructor and nested `RegistrationClientHandler.channelRead`, `validMessageLength`, `handle(RpcDeniedReply)`, and `handle(RpcAcceptedReply, XDR)`.

Control flow: inherits connection setup from `SimpleTcpClient`. On read, the handler validates a minimum response size, parses the TCP record mark, copies the reply payload into an XDR buffer, reads an `RpcReply`, handles denied vs accepted replies, expects `SUCCESS`, reads the boolean answer, logs result, and closes the channel.

State and persistence: stateless beyond request inherited from `SimpleTcpClient`; no persistence.

Dependencies and integration: used by ONC RPC registration paths. Depends on `RpcReply`, `RpcAcceptedReply`, `RpcDeniedReply`, `XDR`, Netty `ByteBuf`, and `SimpleTcpClientHandler`.

Risks: uses assertions for fragment size and success state; assertions may be disabled. It assumes array-backed `ByteBuf`. It logs failures but does not surface a boolean result to callers.

Test signals: portmap and registration integration tests should cover accepted, denied, and malformed short responses.

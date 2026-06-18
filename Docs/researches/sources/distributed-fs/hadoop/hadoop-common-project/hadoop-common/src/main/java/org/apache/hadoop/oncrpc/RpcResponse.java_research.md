# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcResponse.java

Purpose: Netty addressed envelope for outbound RPC response bytes.

Important APIs/types/functions: constructors, `data`, and `remoteAddress`.

Control flow: delegates all envelope behavior to `DefaultAddressedEnvelope`; TCP and UDP response stages consume it differently.

State and persistence: wraps a `ByteBuf`, recipient, and optional sender; no persistence.

Dependencies and integration: emitted by `RpcProgram`, `RpcProgramPortmap`, and cache replay code; consumed by `RpcUtil` response stages.

Risks: ByteBuf reference ownership must be consistent. UDP response code assumes recipient is an `InetSocketAddress`.

Test signals: covered indirectly by RPC utility, server, and portmap tests.

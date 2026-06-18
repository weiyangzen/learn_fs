# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcInfo.java

Purpose: immutable carrier for a parsed RPC request plus Netty channel and remote-address context.

Important APIs/types/functions: constructor, `header`, `data`, `channel`, and `remoteAddress`.

Control flow: no logic beyond storing references. Created by `RpcUtil.RpcMessageParserStage` and consumed by `RpcProgram` or `RpcProgramPortmap`.

State and persistence: holds a `RpcMessage`, request `ByteBuf`, Netty `Channel`, and remote `SocketAddress`; no persistence. ByteBuf lifetime is managed by downstream handlers.

Dependencies and integration: links protocol parsing to Netty server handlers.

Risks: constructor accepts a `ChannelHandlerContext` parameter but does not store it. Consumers must release `data` exactly once; `RpcProgram` does so in finally, but custom handlers must be careful.

Test signals: covered by parser and server tests.

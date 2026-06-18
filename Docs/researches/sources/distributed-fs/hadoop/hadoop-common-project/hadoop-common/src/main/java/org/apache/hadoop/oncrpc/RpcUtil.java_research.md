# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcUtil.java

Purpose: utility and sharable Netty stages for ONC RPC xid generation, TCP fragment decoding, RPC message parsing, and TCP/UDP response encoding.

Important APIs/types/functions: `getNewXid`, `sendRpcResponse`, `constructRpcFrameDecoder`, constants `STAGE_RPC_MESSAGE_PARSER`, `STAGE_RPC_TCP_RESPONSE`, `STAGE_RPC_UDP_RESPONSE`, nested `RpcFrameDecoder`, `RpcMessageParserStage`, `RpcTcpResponseStage`, and `RpcUdpResponseStage`.

Control flow: TCP frame decoder waits for a 4-byte record mark and full fragment, then retains and emits the fragment. Parser handles both `DatagramPacket` and TCP `ByteBuf`, builds an XDR read view, parses `RpcCall`, slices remaining bytes as procedure data, and releases malformed buffers. TCP response prepends a last-fragment record mark; UDP response wraps bytes in a datagram to the recipient.

State and persistence: static xid seed initialized from current time; frame decoder tracks `isLast`. No persistence.

Dependencies and integration: central to `SimpleTcpServer`, `SimpleUdpServer`, `Portmap`, and `SimpleTcpClient`. Depends on Netty and `XDR`.

Risks: `getNewXid` is not synchronized/atomic. `RpcFrameDecoder` does not assemble multi-fragment messages into one buffer despite tracking last-fragment state. Parser data slice lifetime depends on downstream retention/release discipline.

Test signals: `TestFrameDecoder` and RPC parser/server tests cover record marks, incomplete frames, malformed calls, and response stages.

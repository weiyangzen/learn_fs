# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/RpcProgramPortmap.java


Purpose: `RpcProgramPortmap` is the Netty handler that implements the ONC RPC portmapper program number `100000`, version `2`, used by Hadoop's RPCB/portmap service. It starts with built-in TCP and UDP mappings for the portmapper itself and maintains runtime program/version/protocol to port registrations.

Important APIs and types: The class is package-private, `@ChannelHandler.Sharable`, and extends Netty `IdleStateHandler`. It exposes portmap constants for `NULL`, `SET`, `UNSET`, `GETPORT`, `DUMP`, and `GETVERSADDR`, stores mappings in `ConcurrentHashMap<String, PortmapMapping>`, tracks active channels through a `ChannelGroup`, and has `getMap()` for tests or package inspection.

Control flow: `channelRead()` casts inbound messages to `RpcInfo`, extracts the `RpcCall`, creates an XDR reader over the request payload, dispatches by procedure id, serializes a reply into a new `XDR`, wraps it in a Netty `ByteBuf`, and sends an `RpcResponse` to the request remote address. `set()` decodes a mapping and stores it, `unset()` removes it, `getport()` returns a matching port or zero, `dump()` serializes all values, and unknown procedures return `PROC_UNAVAIL`.

State and persistence: All state is in-memory and process-local. There is no disk persistence, authentication, or durable recovery; restarting the portmap service resets registrations to the two defaults. The map is concurrent, but procedure handling does not validate ownership or reject replacement of existing keys despite the comment describing refusal of duplicate mappings.

Dependencies and integration: It depends on Hadoop ONC RPC classes (`RpcCall`, `RpcInfo`, `RpcAcceptedReply`, `RpcUtil`, `XDR`), portmap request/response/mapping helpers, Netty channels, and SLF4J. It integrates with the server pipeline by adding active channels to the group and closing idle or exceptional channels.

Risks and test signals: Tests should exercise all procedure ids, duplicate `SET` behavior, `GETVERSADDR` aliasing to `GETPORT`, unknown procedure replies, idle close behavior, and concurrent `SET`/`UNSET` visibility. Security-sensitive deployments should note that the class accepts registration mutations from any caller reaching the handler.

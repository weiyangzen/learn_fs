# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection_impl.cc

Purpose: implements non-template `RpcConnection` logic: handshake/auth/context progression, response parsing, request creation/queueing, packet construction for handshake/context, comms error handling, timeouts, and event hooks.

Important APIs and functions: `AddHeadersToPacket`, constructor/destructor, `GetIoService`, `StartReading`, `HandshakeComplete`, `AuthComplete`, `AuthComplete_locked`, `ContextComplete`, `AsyncFlushPendingRequests`, `HandleRpcResponse`, `HandleRpcTimeout`, `PrepareHandshakePacket`, `PrepareContextPacket`, `AsyncRpc`, `AsyncRpc_locked`, `SendRpcRequests`, `PreEnqueueRequests`, `PrependRequests_locked`, setters, `CommsError`, `ClearAndDisconnect`, `RemoveFromRunningQueue`, and `ToString`.

Control flow: after socket-level handshake succeeds, connection enters authenticating. If SASL is required and compiled, `SaslProtocol::Authenticate` runs; otherwise unsecured auth completes. Context packet is sent, state becomes connected, and pending requests flush. Responses are parsed into `RpcResponseHeaderProto`, matched to sent requests, and callbacks are posted on the `IoService`. Standby exceptions prepend the request and trigger comms error for failover.

State and persistence: manipulates in-memory queues, current response buffers, connection state, auth info, SASL protocol object, and timers. No disk persistence.

Dependencies and integration: depends on Hadoop RPC/context protobufs, `RpcEngine`, `SaslProtocol`, protobuf coded streams, Boost ASIO, and event injection hooks. Template socket operations live in `rpc_connection_impl.h`.

Risks and test signals: `PrepareContextPacket` sets RPC header client id from `client_name` rather than `client_id`, which should be verified against protocol expectations. `HandleRpcTimeout` calls request callback while holding the connection lock, unlike the no-lock callback rule. Standby exception retry prepends a request and calls `CommsError`; tests should cover failover and duplicate response races.

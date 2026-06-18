# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection.h

Purpose: declares the `RpcConnection` abstraction for a persistent NameNode connection with multiplexed in-flight RPCs and ordered response handling.

Important APIs and types: connection lifecycle methods `Connect`, `ConnectAndFlush`, `Disconnect`, handshake/context methods, send/receive completion hooks, `FlushPendingRequests`, `AsyncRpc`, request enqueue helpers, event/auth setters, timeout/error handling, and response state structures/queues.

Control flow: concrete implementations connect sockets, send handshake and context, queue requests, write packets one at a time, read length-prefixed responses, match by call id, and return communication errors to `RpcEngine` for retry.

State and persistence: connection state enum, weak engine pointer, auth info, SASL protocol, pending/auth/sent request queues, outgoing request, current response parser state, event handlers, cluster name, and `connection_state_lock_`. No disk persistence.

Dependencies and integration: depends on `Request`, auth info, event handlers, status, Boost TCP/system types, protobuf response parsing in implementation, and `LockFreeRpcEngine`.

Risks and test signals: lock ordering is documented: engine lock before connection lock, and callbacks must not run while holding locks. Tests should cover concurrent RPC enqueue, unknown call ids, disconnect while pending, timeout removal, and callbacks posted outside locks.

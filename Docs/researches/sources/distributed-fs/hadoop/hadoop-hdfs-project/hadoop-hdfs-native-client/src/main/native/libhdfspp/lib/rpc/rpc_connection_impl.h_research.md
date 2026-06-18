# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection_impl.h

Purpose: defines the template `RpcConnectionImpl<Socket>` for concrete Boost ASIO socket I/O.

Important APIs and functions: constructor/destructor, `Connect`, `ConnectAndFlush`, `ConnectComplete`, `SendHandshake`, `SendContext`, `OnSendCompleted`, `FlushPendingRequests`, `OnRecvCompleted`, and `Disconnect`.

Control flow: `ConnectAndFlush` selects an endpoint, starts async connect, and arms a connect timeout. `ConnectComplete` cancels the timer, tries additional endpoints on failure, or starts reading and sends handshake on success. `FlushPendingRequests` chooses auth or normal queues depending on state, serializes a request, starts its timeout, and writes it. `OnRecvCompleted` drives a three-stage read state: length, content, parse response.

State and persistence: stores options, current/additional endpoints, socket, connect timer, inherited queues/state, and auth/event data. Runtime only.

Dependencies and integration: depends on Boost ASIO sockets/timers/read/write, `RpcConnection`, `RpcEngine`, `Request`, auth info, logging, utility socket disconnect helpers, and `IoService`.

Risks and test signals: connect timer handler calls `ConnectComplete` with host-unreachable when not canceled, so old async operations must be ignored by endpoint/state checks. `FlushPendingRequests` assumes connection lock is held and uses request timers with weak connection/request captures. Tests should cover endpoint fallback, connect timeout, write/read errors, empty payload null requests, and operation-aborted reads during shutdown.

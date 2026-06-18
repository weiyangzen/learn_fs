# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/request.cc

Purpose: implements RPC request packet construction and response callback dispatch.

Important APIs and functions: protobuf helpers `AddHeadersToPacket`, `ConstructPayload`, `SetRequestHeader`; `Request` constructors; `GetPacket`; `OnResponseArrived`; `GetDebugString`; `IncrementFailoverCount`.

Control flow: normal requests serialize the protobuf payload at construction. `GetPacket` builds an RPC request header and method header, then writes length-prefixed delimited protobuf headers plus payload. SASL requests omit the method request header. Null requests represent connection tracking and generate no payload, causing immediate callback completion in the connection layer.

State and persistence: stores weak engine, method name, call id, deadline timer, serialized payload, handler, retry count, and failover count. State is per request and in-memory only.

Dependencies and integration: depends on Hadoop RPC header protobufs, `RpcEngine` lock-free metadata, `SaslProtocol` method name, protobuf coded streams, and `IoService` timers. Used by `RpcConnection` queues and retry logic.

Risks and test signals: if `client_id()` generation failed, header construction logs and returns with a partly initialized header. Retry count is reset on failover via `IncrementFailoverCount`. Tests should validate packet bytes for normal, SASL, and null requests; retry/failover counters; and timer cancellation on response.

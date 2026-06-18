# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/request.h

Purpose: declares `Request`, internal bookkeeping for an outstanding NameNode RPC.

Important APIs and types: `Handler`, normal and null constructors, `call_id`, `method_name`, `timer`, `IncrementRetryCount`, `IncrementFailoverCount`, `GetPacket`, `OnResponseArrived`, `get_failover_count`, and `GetDebugString`.

Control flow: `RpcConnection` constructs requests, queues them, asks for serialized packets, starts request timers, and invokes `OnResponseArrived` after parsing a response or error.

State and persistence: weak engine pointer, method name, call id, Boost deadline timer, payload string, response handler, retry count, and failover count. Not thread-safe and intended to be accessed by one connection/engine path at a time.

Dependencies and integration: depends on status, utilities, protobuf message/coded-stream APIs, and Boost deadline timers. It is central to retry and response correlation.

Risks and test signals: weak engine access can fail during filesystem destruction, producing errors instead of packets. Tests should cover request lifetime during shutdown, no-retry policy initialization, and not-thread-safe assumptions under connection locking.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_engine.h

Purpose: declares `RpcEngine` and `LockFreeRpcEngine`, the central thread-safe RPC coordinator and the restricted interface connections can call while holding their own locks.

Important APIs and types: RPC version/call-id constants, `Connect`, `CancelPendingConnect`, `AsyncRpc`, `Shutdown`, `AsyncRpcCommsError`, `RpcCommsError`, retry/client/protocol accessors, test hooks, `SetFsEventCallback`, connection factory methods, and HA endpoint state.

Control flow: generated stubs call `AsyncRpc`; connections call lock-free metadata and comms-error callbacks; engine owns retry/failover decisions and connection replacement.

State and persistence: shared current connection, `IoService`, options, client identity, protocol metadata, retry policy, auth info, cluster name, atomic call ID, retry timer, event handlers, engine mutex, cancellation flag, last endpoints, and optional HA tracker. Runtime only.

Dependencies and integration: includes options/status, auth/retry/event/util helpers, NameNode tracker, protobuf message lite, Boost TCP/timer, atomics/mutexes. It integrates filesystem NameNode operations with transport-level RPC.

Risks and test signals: the header’s lock-order note is a key correctness contract. Tests and reviews should check that new code does not call engine-locking methods from connection-locked paths and that callbacks are not invoked under internal locks.

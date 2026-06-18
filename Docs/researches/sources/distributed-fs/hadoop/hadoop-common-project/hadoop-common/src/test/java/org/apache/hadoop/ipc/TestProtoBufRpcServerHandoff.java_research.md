# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRpcServerHandoff.java

Purpose: verifies protobuf server-side deferred response handoff, where a handler returns before a response is supplied from another thread.

Important APIs/types/functions: `TestProtoBufRpcServerHandoffProtocol`, `TestProtoBufRpcServerHandoffServer`, `ProtobufRpcEngine2.Server.registerForDeferredResponse2()`, `ProtobufRpcEngineCallback2`, generated `TestProtobufRpcHandoffProto`, `ClientInvocationCallable`, and RPC metrics for deferred processing.

Control flow: setup creates a one-handler protobuf RPC server. The server `sleep` method registers for deferred response, starts a `SubjectInheritingThread`, sleeps for the requested duration, and later calls `callback.setResponse()`. Tests submit two concurrent 5s calls and assert completion times are close and total elapsed time is under 7s, proving the single handler was handed off. Metrics tests assert deferred processing and normal processing counters update.

State and persistence behavior: static config/server/address hold per-test state; response timing is returned in protobuf fields. Deferred callback state is in-memory and completed by worker threads. No durable state.

Dependencies and integration points: covers the connection between protobuf RPC engine callbacks, handler accounting, `SubjectInheritingThread`, and `RpcMetrics` (`DeferredRpcProcessingTimeNumOps`, `RpcProcessingTimeNumOps`).

Risks and test signals: wall-clock thresholds are timing-sensitive but directly capture the intended behavior. A failure usually means deferred response registration, callback completion, handler release, or deferred metrics changed.

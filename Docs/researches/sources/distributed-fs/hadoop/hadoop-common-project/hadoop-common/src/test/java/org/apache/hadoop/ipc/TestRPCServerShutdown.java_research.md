# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCServerShutdown.java

Purpose: verifies RPC server shutdown behavior when the handler and call queue are saturated.

Important APIs/types/functions: `TestRpcBase`, `RPC.Builder`, `TestRpcService.sleep()`, `CallQueueManager`, `PBServerImpl`, `CommonConfigurationKeys.IPC_CLIENT_CONNECT_MAX_RETRIES_KEY`, executor futures, and `RPC.stopProxy()/server.stop()` through `stop()`.

Control flow: creates a one-handler server with queue size one and no client connect retries, submits three long sleep RPCs, waits until one call is queued and expected worker threads are active, then stops server/proxy. Each future is expected to fail with a `ServiceException` whose cause is an `IOException` rather than return normally.

State and persistence behavior: local executor, future list, server queue, and client proxy state only. The test tears down the executor in a nested `finally`. No persistent state.

Dependencies and integration points: protects shutdown interaction between handler threads, call queue manager, protobuf service implementation, client futures, and server stop semantics.

Risks and test signals: timing loop depends on thread names/counting from `TestRpcBase.countThreads()`. Strong signal that server stop unblocks queued/in-flight clients with IO failure and does not hang when the queue is full.

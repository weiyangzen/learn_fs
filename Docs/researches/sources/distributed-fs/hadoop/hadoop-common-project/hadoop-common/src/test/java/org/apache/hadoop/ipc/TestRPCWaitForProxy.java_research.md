# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCWaitForProxy.java

Purpose: verifies that `RPC.getProxy()`/first-call connection waiting handles timeouts and interruption correctly.

Important APIs/types/functions: `RpcThread extends SubjectInheritingThread`, `RPC.getProxy()`, `TestRpcService`, `ProtobufRpcEngine2`, retry configuration keys `IPC_CLIENT_CONNECT_MAX_RETRIES_KEY` and `IPC_CLIENT_CONNECT_MAX_RETRIES_ON_SOCKET_TIMEOUTS_KEY`, `ConnectException`, `InterruptedIOException`, and `ClosedByInterruptException`.

Control flow: setup binds the test service to protobuf engine 2. `testWaitForProxy()` starts a worker with zero retries against an invalid port and expects a connection failure. `testInterruptedWaitForProxy()` starts a worker with many retries, waits until it begins, interrupts it, and accepts interruption-related root causes.

State and persistence behavior: worker thread stores `caught` throwable and `waitStarted` flag. Static config is reused. No durable state.

Dependencies and integration points: covers proxy creation, connection retry loops, interrupt propagation through NetUtils/socket code, and subject-inheriting thread behavior.

Risks and test signals: root cause unwrapping is intentionally flexible because exception wrapping changes over time. The test strongly signals that wait-for-proxy does not ignore interrupts or spin indefinitely.

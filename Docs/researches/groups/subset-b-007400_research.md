# subset-b-007400 IPC Test Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestFairCallQueue.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestFairCallQueue.java

Purpose: exercises `FairCallQueue<Schedulable>` as both Hadoop IPC scheduling machinery and a `BlockingQueue` implementation. It validates subqueue capacity allocation, priority spillover, multiplexer-driven dequeue order, overflow exception semantics, blocking put/take behavior, JMX exposure, and metrics.

Important APIs/types/functions: `FairCallQueue`, `Schedulable`, `RpcMultiplexer`, `CallQueueManager.CallQueueOverflowException`, `RpcServerException`, `RetriableException`, `StandbyException`, `UserIdentityProvider`, `Putter`, and `Taker`. The local `mockCall()` helper builds priority-tagged schedulables with mocked `UserGroupInformation`.

Control flow: setup builds a two-level queue under namespace `ns`. Tests then construct queues with custom level counts, capacities, and weights; enqueue mocked calls; override the multiplexer index when deterministic polling is required; and assert which internal `offerQueue`/`putQueue` paths are used. Overflow tests fill each subqueue and verify whether `add()` produces retryable, fatal, or failover-triggering exceptions. Blocking tests use `SubjectInheritingThread` plus latches to prove `put` blocks when full and `take` blocks when empty.

State and persistence behavior: queue state is entirely in-memory, split across priority subqueues. Tests assert aggregate `size()` and `remainingCapacity()` as calls move among queues. No durable state is written, but the queue registers runtime MXBean and metrics state (`QueueSizes`, `FairCallQueueSize_pN`, `FairCallQueueOverflowedCalls_pN`), making cleanup and namespace reuse relevant between tests.

Dependencies and integration points: integrates with Hadoop `Configuration` keys for IPC priority levels, Hadoop metrics assertions, platform MBeanServer, Mockito spies/mocks, `UserGroupInformation`, and IPC exception classes consumed by RPC clients. It indirectly documents how scheduler priority, user identity, queue overflow, and client retry/failover behavior connect.

Risks and test signals: strong coverage of capacity accounting, priority fairness fallback, queue-full error mapping, metrics, and MXBean behavior. Concurrency tests are latch-based but still depend on thread scheduling; MBean object naming can be sensitive to duplicate registration if queue lifecycle changes. A notable test signal is the distinction between non-lowest priority overflow (`ERROR`/retriable) and lowest-priority overflow (`FATAL`) plus the failover mode that wraps `StandbyException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestFairCallQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIPC.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIPC.java

Purpose: broad low-level IPC regression suite for Hadoop's writable-based `Client`/`Server` stack. It covers echo calls, auxiliary listeners, serialization failures, connection setup failures, socket/read/write timeouts, reader queue saturation, idle cleanup, call IDs and retry counts, legacy wire compatibility, response limits, user binding, and address resolution behavior.

Important APIs/types/functions: local `TestServer extends Server`, `SerialCaller`, `TestInvocationHandler`, `TestInvalidTokenHandler`, injected fault writables (`IOEOnReadWritable`, `RTEOnReadWritable`, `IOEOnWriteWritable`, `RTEOnWriteWritable`), `Client.ConnectionId`, `Server.Call`, `Server.Connection`, `AlignmentContext`, `RetryProxy`, `DefaultFailoverProxyProvider`, `NetworkTraces`, and helpers `call()`, `doErrorTest()`, `checkBlocking()`, `doIpcVersionTest()`.

Control flow: each test creates an in-process IPC server and one or more clients. Normal echo tests issue concurrent calls and verify returned `LongWritable` values. Fault tests inject exceptions at client write, server read, server response write, or client response read, then disable faults and prove the connection/server remains usable. Queue pressure tests block handlers and readers with latches, then flood clients to confirm listener backpressure. Retry tests use proxies and server call listeners to observe call ID/retry propagation. Wire compatibility tests open raw sockets, write captured old Hadoop RPC dumps or HTTP GET bytes, and compare exact response bytes.

State and persistence behavior: all state is process-local: static configuration, writable fault flags, server call listener callbacks, connection maps, open sockets, retry call thread-locals, and static network trace byte arrays. Tests explicitly reset UGI/security config before each test, clear interrupt status after interrupt cleanup checks, reset static resolution side effects, and stop clients/servers to avoid socket/thread leakage.

Dependencies and integration points: integrates with `CommonConfigurationKeys`, `NetUtils`, `SecurityUtil`, `UserGroupInformation`, retry policy APIs, protobuf response headers for call ID checks, Mockito, AssertJ, `GenericTestUtils`, and Hadoop's raw IPC protocol constants. It is a key contract test for server listener/readers, client connection cache, connection ID mutability, security-aware socket binding, alignment response processing, and backward-compatible version mismatch diagnostics.

Risks and test signals: heavy concurrency/time-based tests can be sensitive to slow hosts, DNS behavior, `/proc/self/fd` availability, and interrupt timing. The suite strongly signals regressions in connection cleanup, half-constructed connection caching, host resolution, old-client wire responses, retry/idempotency semantics, and max-response enforcement. It also documents that invalid tokens should not be retried, stopped clients must reject later calls, and `ConnectionId.hashCode()` must remain stable after address resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIPC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIPCServerResponder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIPCServerResponder.java

Purpose: stresses IPC server response writing, especially partial socket writes and deferred response handling. It proves the responder can serve many clients with small send buffers and that handlers are released when responses are postponed.

Important APIs/types/functions: local `TestServer extends Server`, `Caller extends SubjectInheritingThread`, static `call(Client, Writable, InetSocketAddress)`, `Server.Call.postponeResponse()`, `Call.sendResponse()`, `BytesWritable`, `IntWritable`, `Client.ConnectionId`, and `Server.getCurCall()`.

Control flow: responder stress tests construct a server returning variable-size `BytesWritable` payloads while socket send buffer size is forced below the maximum payload, then spawn caller threads that repeatedly send random byte arrays. `testDeferResponse()` uses a one-handler server whose call method postpones a response zero, one, or two times based on an integer request; futures verify the client remains blocked until enough `sendResponse()` calls occur, while intervening immediate calls prove the handler is free.

State and persistence behavior: uses static byte arrays and mutable static `Configuration`; `testResponseBuffer()` mutates `Server.INITIAL_RESP_BUF_SIZE` and `IPC_SERVER_RPC_MAX_RESPONSE_SIZE_KEY` to force tiny response buffers, then resets configuration. Deferred-response state lives in `Server.Call` objects retained by test references until explicitly released.

Dependencies and integration points: integrates with the low-level writable IPC client/server path, response buffer sizing configuration, responder thread behavior, executor futures, latches, and Hadoop socket utilities. It is an integration point between handler execution and responder-side asynchronous write completion.

Risks and test signals: partial-write behavior is timing/socket-buffer sensitive. The strongest signal is that response ordering and sequence numbers remain correct while deferred calls are pending, and that one handler can continue processing new calls after `postponeResponse()`. Missing cleanup of executor/client/server resources would make failures noisy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIPCServerResponder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIdentityProviders.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIdentityProviders.java

Purpose: verifies pluggable IPC identity provider loading and default user identity extraction from a `Schedulable`.

Important APIs/types/functions: `IdentityProvider`, `UserIdentityProvider`, `Schedulable`, `CommonConfigurationKeys.IPC_IDENTITY_PROVIDER_KEY`, `Configuration.getInstances()`, `UserGroupInformation`, and local `FakeSchedulable`.

Control flow: one test sets the identity provider config key to `UserIdentityProvider`, loads provider instances, and checks type/size. The second creates `UserIdentityProvider`, asks it to make an identity for `FakeSchedulable`, compares that to the current UGI username, and verifies the default `Schedulable.getCallerContext()` path throws `UnsupportedOperationException`.

State and persistence behavior: no persistent state. The only mutable state is a local `Configuration`; current-user lookup depends on process security context.

Dependencies and integration points: ties call scheduling identity to Hadoop configuration plugin loading and UGI. This is used by fair/decay schedulers and queue metrics that group work by caller identity.

Risks and test signals: small but important signal that provider class names remain loadable through configuration and that default schedulable identity remains username-based. The current-user dependency can vary by test environment but should be stable under Hadoop's test UGI setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIdentityProviders.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestMiniRPCBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestMiniRPCBenchmark.java

Purpose: smoke-tests `MiniRPCBenchmark` under simple authentication.

Important APIs/types/functions: `MiniRPCBenchmark`, `Configuration`, and SLF4J `Level`.

Control flow: the single test sets `hadoop.security.authentication` to `simple`, constructs the benchmark with DEBUG logging, and runs a small benchmark iteration count with null keytab/principal inputs.

State and persistence behavior: no durable state; benchmark creates temporary in-process RPC client/server resources internally and relies on its own cleanup.

Dependencies and integration points: validates the benchmark utility can run in the unsecured local test environment. It indirectly covers benchmark setup around RPC, UGI, and logging.

Risks and test signals: signal is coarse: return without exception. It may catch broken benchmark wiring but not performance regressions. Runtime can be environment-sensitive if the benchmark's internal networking setup changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestMiniRPCBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestMultipleProtocolServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestMultipleProtocolServer.java

Purpose: verifies that a server initialized through `TestRpcBase` can host protobuf RPC service traffic, historically covering mixed protocol support on one server.

Important APIs/types/functions: `TestRpcBase`, `RPC.Server`, `RPC.setProtocolEngine()`, `ProtobufRpcEngine2`, `TestRpcService`, and `TestProtoBufRpc.testProtoBufRpc()`.

Control flow: setup initializes common RPC test configuration and starts a test server with two handlers. The test configures a protobuf RPC engine for `TestRpcService`, obtains a proxy to the inherited server address, and reuses the canonical protobuf ping/echo/error assertions from `TestProtoBufRpc`.

State and persistence behavior: only static test server state and inherited address/configuration are maintained; teardown stops the server. No files or durable state.

Dependencies and integration points: bridges the generic RPC test base and protobuf RPC suite, ensuring server protocol registration remains compatible with clients configured separately.

Risks and test signals: compact integration smoke test. Failures point to protocol engine registration, server multi-protocol wiring, or changes in `TestRpcBase` setup rather than detailed protobuf method behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestMultipleProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProcessingDetails.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProcessingDetails.java

Purpose: unit-tests `ProcessingDetails`, the timing container used to record IPC lifecycle durations.

Important APIs/types/functions: `ProcessingDetails`, `ProcessingDetails.Timing`, `TimeUnit`, `set()`, `add()`, `get()`, and `toString()`.

Control flow: `testTimeConversion()` creates a microsecond-based details object, stores enqueue time in base units, stores/adds queue time using milliseconds and microseconds, then verifies conversion to nanoseconds and seconds. `testToString()` checks the exact textual field order and converted values.

State and persistence behavior: state is a fixed set of timing counters stored in the `ProcessingDetails` instance. No persistence.

Dependencies and integration points: feeds RPC metrics/logging/reporting paths that expect stable timing names and units. The exact string output is a compatibility contract for diagnostics.

Risks and test signals: exact-string assertion will catch field order/name changes. Conversion tests catch truncation and base-unit mistakes, but only cover a few timing fields directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProcessingDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRPCCompatibility.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRPCCompatibility.java

Purpose: validates protobuf RPC protocol-version compatibility and optional-field evolution behavior.

Important APIs/types/functions: `OldRpcService`, `NewRpcService`, `NewerRpcService`, `ProtocolInfo`, generated protobuf service interfaces (`OldProtobufRpcProto`, `NewProtobufRpcProto`, `NewerProtobufRpcProto`), `Server.getClientId()`, and `ProtobufRpcEngine2`.

Control flow: the test starts a server implementing version 2 of protocol name `testProto`, then creates a version 1 client for the same protocol and verifies a ping fails with a version mismatch. It then creates a newer version-2 compatible client and verifies an `echo` call with the old empty request remains compatible.

State and persistence behavior: static address/server/config fields hold test process state. Server implementations inspect per-call client ID state and assert the expected 16-byte ID. No durable persistence.

Dependencies and integration points: exercises protocol name/version annotations, generated protobuf blocking services, RPC builder registration, client ID propagation, and compatibility of protobuf schema evolution.

Risks and test signals: strong signal for version mismatch diagnostics and optional field compatibility. It does not deeply test all method evolution cases; server cleanup is not in a `finally`, so unexpected early failures could leave the static server running in-process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRPCCompatibility.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRpc.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRpc.java

Purpose: primary protobuf RPC suite for `ProtobufRpcEngine2`, also testing coexistence with the legacy protobuf engine. It covers ping/echo/error calls, second protocol registration, legacy service registration order, RPC metrics, maximum data length, application exception mapping, and slow-RPC logging.

Important APIs/types/functions: `TestRpcService2`, `TestRpcService2Legacy`, `PBServer2Impl`, `PBServer2ImplLegacy`, `RPC.Builder`, `server.addProtocol()`, generated `TestProtobufRpcProto`/`TestProtobufRpc2Proto`, `ProtobufRpcEngine2`, legacy `ProtobufRpcEngine`, `RpcMetrics`, and parameter source `params()`.

Control flow: each parameterized test calls `initTestProtoBufRpc()` with combinations of legacy enabled and legacy-first registration. Setup configures max data length and slow RPC logging, registers protobuf engines, builds a server with one protocol, adds a second protocol, optionally adds a legacy protocol, and starts it. Tests then obtain proxies and issue ping/echo/error/sleep calls while asserting response contents, `RemoteException` error codes, metrics counters, oversized request failure, and slow-call metric increments.

State and persistence behavior: static server/address plus per-test booleans define runtime state. `@AfterEach` stops the server. No persistent state. Metrics accumulate on the in-process server and are inspected after call bursts.

Dependencies and integration points: integrates protobuf generated classes from both shaded/current and legacy protobuf packages, Hadoop metrics, `CommonConfigurationKeys.IPC_MAXIMUM_DATA_LENGTH`, slow-RPC logging controls, and `TestRpcBase` helpers.

Risks and test signals: parameterization gives good coverage of protocol registration order and mixed engines. Slow-RPC tests use 10K fast calls and wall-clock sleeps, so they are more timing-sensitive. Key signals are correct error-code classification (`ERROR_RPC_SERVER`, `ERROR_APPLICATION`), data-length rejection, detailed metric method counters, and disabled slow logging producing no slow-call increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRpc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRpcServerHandoff.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRpcServerHandoff.java

Purpose: verifies protobuf server-side deferred response handoff, where a handler returns before a response is supplied from another thread.

Important APIs/types/functions: `TestProtoBufRpcServerHandoffProtocol`, `TestProtoBufRpcServerHandoffServer`, `ProtobufRpcEngine2.Server.registerForDeferredResponse2()`, `ProtobufRpcEngineCallback2`, generated `TestProtobufRpcHandoffProto`, `ClientInvocationCallable`, and RPC metrics for deferred processing.

Control flow: setup creates a one-handler protobuf RPC server. The server `sleep` method registers for deferred response, starts a `SubjectInheritingThread`, sleeps for the requested duration, and later calls `callback.setResponse()`. Tests submit two concurrent 5s calls and assert completion times are close and total elapsed time is under 7s, proving the single handler was handed off. Metrics tests assert deferred processing and normal processing counters update.

State and persistence behavior: static config/server/address hold per-test state; response timing is returned in protobuf fields. Deferred callback state is in-memory and completed by worker threads. No durable state.

Dependencies and integration points: covers the connection between protobuf RPC engine callbacks, handler accounting, `SubjectInheritingThread`, and `RpcMetrics` (`DeferredRpcProcessingTimeNumOps`, `RpcProcessingTimeNumOps`).

Risks and test signals: wall-clock thresholds are timing-sensitive but directly capture the intended behavior. A failure usually means deferred response registration, callback completion, handler release, or deferred metrics changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRpcServerHandoff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPC.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPC.java

Purpose: broad high-level RPC facade test suite, primarily around protobuf RPC services through `RPC`, `RPC.Builder`, server/client lifecycle, authorization, metrics, interruption, backoff, slow connections, external calls, protocol engine selection, and request-kind validation.

Important APIs/types/functions: `TestProtocol`/`TestImpl`, `StoppedProtocol`, `StoppedRpcEngine`, `StoppedInvocationHandler`, `Transactions`, `SlowRPC`, `MockOutputStream`, `ExternalCall`, `RPC.getProxy()`, `RPC.stopProxy()`, `RPC.Builder`, `ProtobufRpcEngine2`, `RpcMetrics`, `DecayRpcScheduler`, `CallQueueManager`, and generated `TestRpcService` protobuf calls inherited from `TestRpcBase`.

Control flow: tests construct in-process RPC servers with varying builder settings, obtain proxies, and issue protobuf calls. Basic call tests verify ping/echo/add/error and multi-threaded data exchange. Authorization tests refresh service ACLs and assert success/failure counters. Interruption/slow-connection tests use barriers, mock sockets/streams, async mode, and future cancellation to verify only intended calls fail. Metrics tests perform large numbers of calls and inspect aggregate, detailed, quantile, per-user, lock-wait, success, processing-time, total-request, and nanos-unit metrics. Backoff tests fill call queues or exceed decay scheduler response-time thresholds and assert retriable exceptions.

State and persistence behavior: state is local to RPC server/client instances, connection caches, metrics registries, thread pools, and test configuration. Several tests mutate static/global RPC engine mapping or client async mode and restore where needed. No durable state is written. Metrics are the main observable stateful integration surface.

Dependencies and integration points: central integration point for `RPC`, protobuf engine registration, Hadoop security/authorization (`PolicyProvider`, `AccessControlException`, `AuthorizationException`), metrics2 assertions, retry policies, socket factories, schedulers, UGI, and server queue internals. It also validates `serverNameFromClass()` naming behavior for nested/anonymous classes.

Risks and test signals: many tests are concurrency and timing sensitive, particularly slow connection, interruption, backoff, scheduler metrics, and total requests per second. Strong signals include no leaked reader threads after stop, correct proxy close behavior even under retry wrappers, insecure-client error code `FATAL_UNAUTHORIZED`, fatal reader exceptions closing connections while nonfatal ones keep them alive, and protobuf-only servers rejecting unregistered `RpcKind` without deserializing payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCCallBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCCallBenchmark.java

Purpose: smoke-tests the `RPCCallBenchmark` command-line tool with protobuf engine settings.

Important APIs/types/functions: `RPCCallBenchmark`, `ToolRunner.run()`, JUnit timeout, and benchmark arguments `--clientThreads`, `--serverThreads`, `--time`, `--serverReaderThreads`, `--messageSize`, `--engine protobuf`.

Control flow: invokes the benchmark tool with 30 client threads, 30 server threads, 5 second duration, 4 server reader threads, 1024-byte messages, and protobuf engine, then asserts exit code 0.

State and persistence behavior: benchmark runtime state is internal to the tool: local server/client threads and timing counters. No persistent output is asserted by this test.

Dependencies and integration points: validates the CLI parser, benchmark setup, protobuf engine path, thread configuration, and ToolRunner integration.

Risks and test signals: coarse signal that benchmark invocation completes successfully under a 20s timeout. It can expose startup/runtime regressions but not detailed throughput or latency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCCallBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCCompatibility.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCCompatibility.java

Purpose: tests method-signature fingerprint compatibility used by versioned RPC protocol negotiation.

Important APIs/types/functions: `VersionedProtocol`, `ProtocolInfo`, `ProtocolSignature`, `TestProtocol0/1/2/3/4`, `TestImpl0/1/2`, `RPC.setProtocolEngine()`, and `ProtobufRpcEngine2`.

Control flow: setup resets `ProtocolSignature` cache and binds all local protocols to protobuf engine 2. The active test reflects methods from protocol interfaces and checks fingerprints differ when method name, return type, parameter type, or parameter count differs, match across declaring classes for identical signatures, and produce order-independent aggregate fingerprints.

State and persistence behavior: static config/server/address fields are present but this file's active coverage is reflection/cache state only. Teardown stops any proxy/server if future tests add them. No durable state.

Dependencies and integration points: method fingerprinting is part of Hadoop RPC compatibility negotiation; protocol annotations allow newer interfaces to share protocol names with older ones.

Risks and test signals: focused signal for accidental fingerprint algorithm changes. It does not perform full client/server compatibility calls in its current form, but protects the core hash behavior those calls rely on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCCompatibility.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCServerShutdown.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCServerShutdown.java

Purpose: verifies RPC server shutdown behavior when the handler and call queue are saturated.

Important APIs/types/functions: `TestRpcBase`, `RPC.Builder`, `TestRpcService.sleep()`, `CallQueueManager`, `PBServerImpl`, `CommonConfigurationKeys.IPC_CLIENT_CONNECT_MAX_RETRIES_KEY`, executor futures, and `RPC.stopProxy()/server.stop()` through `stop()`.

Control flow: creates a one-handler server with queue size one and no client connect retries, submits three long sleep RPCs, waits until one call is queued and expected worker threads are active, then stops server/proxy. Each future is expected to fail with a `ServiceException` whose cause is an `IOException` rather than return normally.

State and persistence behavior: local executor, future list, server queue, and client proxy state only. The test tears down the executor in a nested `finally`. No persistent state.

Dependencies and integration points: protects shutdown interaction between handler threads, call queue manager, protobuf service implementation, client futures, and server stop semantics.

Risks and test signals: timing loop depends on thread names/counting from `TestRpcBase.countThreads()`. Strong signal that server stop unblocks queued/in-flight clients with IO failure and does not hang when the queue is full.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCServerShutdown.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCWaitForProxy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCWaitForProxy.java

Purpose: verifies that `RPC.getProxy()`/first-call connection waiting handles timeouts and interruption correctly.

Important APIs/types/functions: `RpcThread extends SubjectInheritingThread`, `RPC.getProxy()`, `TestRpcService`, `ProtobufRpcEngine2`, retry configuration keys `IPC_CLIENT_CONNECT_MAX_RETRIES_KEY` and `IPC_CLIENT_CONNECT_MAX_RETRIES_ON_SOCKET_TIMEOUTS_KEY`, `ConnectException`, `InterruptedIOException`, and `ClosedByInterruptException`.

Control flow: setup binds the test service to protobuf engine 2. `testWaitForProxy()` starts a worker with zero retries against an invalid port and expects a connection failure. `testInterruptedWaitForProxy()` starts a worker with many retries, waits until it begins, interrupts it, and accepts interruption-related root causes.

State and persistence behavior: worker thread stores `caught` throwable and `waitStarted` flag. Static config is reused. No durable state.

Dependencies and integration points: covers proxy creation, connection retry loops, interrupt propagation through NetUtils/socket code, and subject-inheriting thread behavior.

Risks and test signals: root cause unwrapping is intentionally flexible because exception wrapping changes over time. The test strongly signals that wait-for-proxy does not ignore interrupts or spin indefinitely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCWaitForProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestResponseBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestResponseBuffer.java

Purpose: unit-tests `ResponseBuffer` framing, resizing, reset, and payload preservation.

Important APIs/types/functions: `ResponseBuffer`, `writeBytes()`, `capacity()`, `size()`, `reset()`, `setCapacity()`, `toByteArray()`, and local `checkBuffer()`.

Control flow: creates a buffer with initial capacity 8, verifies empty framing, writes two strings, verifies concatenated payload, resets without shrinking, explicitly shrinks capacity, writes again, and decodes `toByteArray()` via `DataInputStream` to assert the first four bytes are payload length followed by exact payload bytes.

State and persistence behavior: buffer maintains in-memory byte array capacity and write position. `reset()` clears logical contents but not array length; `setCapacity()` changes backing array size. No persistence.

Dependencies and integration points: documents response framing expected by IPC responders and clients: length-prefixed payload bytes.

Risks and test signals: strong low-level signal for wire framing and buffer reuse semantics. It does not test very large payload growth or error cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestResponseBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRetryCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRetryCache.java

Purpose: tests `RetryCache` behavior for idempotent server operations under concurrent retries, covering success/failure and long/short operation timing.

Important APIs/types/functions: `RetryCache`, `RetryCache.CacheEntryWithPayload`, `RetryCache.waitForCompletion()`, `RetryCache.setState()`, `Server.Call`, `Server.getCurCall()`, `ClientId.getClientId()`, and local `TestServer.echo()`.

Control flow: `newCall()` creates a synthetic call with stable client ID and call ID. `TestServer.echo()` waits for/creates a retry cache entry, returns cached payload for successful completed entries, otherwise increments operation count, optionally sleeps, sets cache state, and returns success or failure output. `testOperations()` starts many threads sharing the same current call and asserts all return expected values plus operation/retry counters.

State and persistence behavior: retry cache state is in-memory with a long expiration period; call identity comes from thread-local current calls. Static `callId`, `CLIENT_ID`, random, and shared `TestServer` persist across tests, while counters reset before each test.

Dependencies and integration points: models how Hadoop RPC servers deduplicate retried idempotent operations by `(clientId, callId)`, and how failed operations are not reused as successful payloads.

Risks and test signals: strong concurrency signal that only one successful operation executes and all other attempts reuse payload, while failed attempts execute independently. Some test names/comments around short success appear inconsistent with the `success` argument, so readers should trust assertions over comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRetryCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRetryCacheMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRetryCacheMetrics.java

Purpose: verifies retry cache metrics names and live counter updates.

Important APIs/types/functions: `RetryCache`, `RetryCacheMetrics`, `MetricsRecordBuilder`, `MetricsAsserts.getMetrics()`, and counters `CacheHit`, `CacheCleared`, `CacheUpdated`.

Control flow: creates a retry cache named `TestRetryCacheMetrics`, checks the metrics record name is `RetryCache.TestRetryCacheMetrics`, then verifies initial counters are zero. It calls `incrCacheHit()`, `incrCacheCleared()`, and `incrCacheUpdated()` on the metrics object and checks expected counter values after each update.

State and persistence behavior: metrics state is in-memory in Hadoop metrics2. The retry cache object owns a metrics source. No persistent state.

Dependencies and integration points: covers the metric naming contract and counter exposure consumed by monitoring systems.

Risks and test signals: focused signal for metrics regressions. Because metric sources can be global, duplicate names or leaked sources in nearby tests could affect this if lifecycle behavior changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRetryCacheMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestReuseRpcConnections.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestReuseRpcConnections.java

Purpose: verifies RPC connection reuse behavior across retry policies, especially that normal retry paths reuse the same client connection while `TRY_ONCE_THEN_FAIL` does not perform extra retries.

Important APIs/types/functions: `TestRpcBase`, `RetryProxy`, `RetryPolicies`, `UnreliableInterface`, `UnreliableImplementation`, `UnreliableException`, `TestRpcService`, `ProtobufRpcEngine2`, and `Client.getConnectionIds()`.

Control flow: setup configures protobuf RPC and resets `UnreliableImplementation` counters. `testDefaultRetryPolicyReuseConnections()` delegates to `verifyRetryPolicyReuseConnections()` with the default retry policy; the helper creates server/proxy, wraps a failover/retry proxy around an unreliable implementation, triggers failing/succeeding calls, and checks the protobuf client's connection ID set size to ensure connection reuse. `testRetryPolicyTryOnceThenFail()` verifies a no-retry policy fails after one unreliable invocation.

State and persistence behavior: connection reuse state lives in the protobuf engine client cache and connection ID set; unreliable operation counters are static/test-local and reset before each test. Servers/proxies are stopped after use.

Dependencies and integration points: ties retry proxy behavior to RPC client connection cache behavior and unreliable protocol semantics.

Risks and test signals: important signal for avoiding connection churn during retries. It is sensitive to shared client cache cleanup; failure to clear/stop proxies could make connection counts misleading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestReuseRpcConnections.java -->

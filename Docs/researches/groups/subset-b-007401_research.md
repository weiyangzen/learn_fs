# subset-b-007401 grouped research

This grouped report covers Hadoop common IPC, JMX, logging, and metrics test sources. Each file section is source-tree aligned and intended for reconciliation into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcBase.java

## Purpose

`TestRpcBase` is the shared fixture for Hadoop IPC protobuf RPC tests. It does not define JUnit test methods itself; instead it centralizes server construction, client proxy creation, token fixtures, test protocol metadata, and a protobuf-backed server implementation used by authentication, scheduling, timeout, and response-ordering tests.

## Important APIs, Types, And Functions

The main helper APIs are `setupConf()`, `newServerBuilder()`, `setupTestServer()`, overloaded `getClient()` methods, `getMultipleClientWithIndex()`, `stop()`, and `countThreads()`. `MockConnectionId` extends `Client.ConnectionId` by adding an `index` into equality/hash identity so tests can force separate cached connections. `TestTokenIdentifier`, `TestTokenSecretManager`, and `TestTokenSelector` provide a minimal Hadoop token kind named `test.token`. `TestRpcService` is annotated with `@KerberosInfo`, `@TokenInfo`, and `@ProtocolInfo` and extends the generated protobuf blocking interface. `PBServerImpl` implements test RPC methods such as `ping`, `echo`, `error`, `slowPing`, `add`, `exchange`, `sleep`, `lockAndSleep`, `getAuthMethod`, auth-user queries, and postponed response methods.

## Control Flow

Tests call `setupConf()` to install `ProtobufRpcEngine2` for `TestRpcService`, build an `RPC.Server` around a reflective protobuf `BlockingService`, start it, and use `NetUtils.getConnectAddress()` for clients. Client helpers call `RPC.getProtocolProxy()` with the current UGI, socket factory, timeout, optional retry policy, and optional fallback-to-simple-auth flag. `PBServerImpl` methods exercise normal response paths, thrown `ServiceException`s, lock timing accumulation through `ProcessingDetails`, server-local context via `Server.get()` and `Server.getCurCall()`, and postponed calls by storing `Server.Call` objects then later invoking `sendResponse()`.

## State And Persistence Behavior

The class has static shared `addr` and `conf` fields, per-server latches and postponed-call lists in `PBServerImpl`, token identity serialized through Hadoop `Writable`, and no persistent disk state. Mutable state is test-scoped but global UGI/protocol-engine configuration can leak if callers do not reset it. `stop()` is intentionally tolerant and attempts to close proxies and servers despite exceptions.

## Dependencies And Integration Points

It integrates with Hadoop RPC core (`RPC`, `Server`, `Client.ConnectionId`, `ClientId`), protobuf test classes under `org.apache.hadoop.ipc.protobuf`, UGI/security/token APIs, `NetUtils`, retry policies, and `ProcessingDetails`. Downstream tests depend on its fixtures to validate SASL, response postponement, user identity propagation, and server timing behavior.

## Risks And Test Signals

Risks include static configuration leakage across tests, cached client connections masking configuration changes, races around postponed calls, and token selector/service mismatches. Strong signals are tests that create real RPC servers, assert client IDs, verify auth methods and users through server context, exercise deferred response ordering, and check lock timing injection through `ProcessingDetails`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcServerHandoff.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcServerHandoff.java

## Purpose

`TestRpcServerHandoff` verifies Hadoop IPC server support for deferring a handler response and completing it later, either with a normal response payload or with a remote exception. This protects the handoff path used when a handler must release itself while another thread eventually finishes the RPC.

## Important APIs, Types, And Functions

`ServerForHandoffTest` subclasses `Server` with `BytesWritable` parameters and overrides `call()` to capture the current `Server.Call`, call `deferResponse()`, signal invocation, and return `null`. Its `sendResponse()` calls `setDeferredResponse(request)` and `sendError()` calls `setDeferredError(new IOException("DeferredError"))`. `ClientCallable` uses low-level `Client.call()` with `RPC.RpcKind.RPC_BUILTIN`.

## Control Flow

Each test starts the custom server, launches a client call in a `FutureTask` on a `SubjectInheritingThread`, waits until the server handler has captured and deferred the call, then repeatedly confirms the future does not complete for roughly three seconds. `testDeferredResponse()` then injects the original request as the deferred response and asserts the client receives the same bytes. `testDeferredException()` injects a deferred error and asserts the client future fails with a `RemoteException` containing `DeferredError`.

## State And Persistence Behavior

The server stores the current request and deferred `Call` in volatile fields, uses an `AtomicBoolean`, `ReentrantLock`, and `Condition` to coordinate handler invocation, and has no persisted state. The important state transition is handler-owned call to externally completed deferred call.

## Dependencies And Integration Points

The test directly exercises `Server.Call.deferResponse()`, `setDeferredResponse()`, `setDeferredError()`, low-level `Client.ConnectionId`, `BytesWritable`, and `NetUtils` address resolution. It complements the protobuf-level postponed response tests in `TestRpcBase` and `TestSaslRPC`.

## Risks And Test Signals

The main risks are handler leaks, premature client completion, missing wakeups, and error serialization mismatches. Test signals are timeout-guarded futures that must block before handoff, equality of `BytesWritable` response payloads, and `RemoteException` propagation for deferred failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcServerHandoff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcWritable.java

## Purpose

`TestRpcWritable` validates `RpcWritable` wrappers for classic Hadoop `Writable` values, shaded protobuf messages, and nested `RpcWritable.Buffer` slices. It protects the byte-buffer decoding contract used by mixed IPC payload formats.

## Important APIs, Types, And Functions

The tests use `RpcWritable.wrap(Writable)`, `RpcWritable.wrap(Message)`, `RpcWritable.Buffer.wrap(ByteBuffer)`, `Buffer.getValue(defaultProto)`, and `Buffer.newInstance(Class, Configuration)`. Test fixtures are a `LongWritable` initialized from `Time.now()` and two `EchoRequestProto` messages.

## Control Flow

The tests serialize a value or sequence of values to a `ByteArrayOutputStream`, wrap the resulting bytes in a `ByteBuffer`, then decode through the appropriate `RpcWritable` path. The nested-buffer test first consumes a `LongWritable`, then extracts the remaining bytes into a nested buffer and decodes two protobuf messages from the slice.

## State And Persistence Behavior

All state is in-memory `ByteBuffer` position and remaining-byte counters. The tests assert that wrapper reads advance the original buffer consistently and that nested buffer extraction drains the parent while preserving the child slice.

## Dependencies And Integration Points

This file integrates with Hadoop `Writable`, shaded protobuf `Message`, generated IPC test protos, `RpcWritable`, and byte-buffer based RPC decoding. It is a low-level serialization compatibility check for both protobuf and legacy writable RPC payloads.

## Risks And Test Signals

Risks include off-by-one buffer consumption, incorrectly handling delimited protobuf messages, parent/child buffer aliasing, and leaving unread bytes. Test signals are object equality, positive remaining-byte assertions between sequential reads, and final `remaining()==0` checks on both parent and nested buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestSaslRPC.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestSaslRPC.java

## Purpose

`TestSaslRPC` is the main SASL-over-Hadoop-RPC integration test. It parameterizes over Hadoop RPC protection/QOP choices and validates token, Kerberos, simple-auth fallback, SASL PLAIN, connection cache, bad-token error, and postponed-response behavior for protobuf RPC.

## Important APIs, Types, And Functions

The class extends `TestRpcBase`. Its parameter source `data()` covers each `QualityOfProtection` plus mixed privacy/authentication cases, including an `AuthSaslPropertiesResolver` that forces server QOP to authentication. Key fixtures include `BadTokenSecretManager`, `CustomSecurityInfo`, `TestPlainCallbacks`, patterns for expected auth failures, `UseToken`, and helpers `createConfForAuth()`, `createServerSecretManager()`, `setupServerUgi()`, `setupClientUgi()`, `setupTokenIfNeeded()`, and `createClientAndQueryAuthMethod()`.

## Control Flow

Each parameterized test calls `initTestSaslRPC()`, which resets configuration to simple auth, sets `hadoop.rpc.protection`, optional SASL resolver class, UGI configuration, global secret-manager flags, fallback behavior, and the protobuf RPC engine. Digest/token tests start a test server with a token secret manager, install a token on the current user, call `getAuthMethod()`, and inspect connection SASL QOP plus server-side `saslServer` retention. The auth matrix starts servers under SIMPLE, TOKEN, or KERBEROS UGIs and creates clients with optional valid, invalid, unrelated, or absent tokens, then compares success or failure strings to expected auth methods and regular expressions.

## State And Persistence Behavior

State is mostly global test configuration: `conf`, UGI authentication configuration, static booleans controlling secret-manager enablement, Java security provider registration for PLAIN, and client connection caches. Token state is held on UGI instances, and tests explicitly stop servers/proxies or clear client connection IDs where cache reuse affects results. There is no durable storage except optional Kerberos keytab use in the manual `main()` path.

## Dependencies And Integration Points

The file exercises `SaslRpcClient`, `SaslRpcServer`, `SaslPlainServer`, UGI, `SecurityUtil`, Hadoop tokens, RPC client fallback flags, `SaslPropertiesResolver`, protobuf RPC service methods from `TestRpcBase`, and `Client.ConnectionId`. It also references HADOOP-17975 and validates a connection-cache fallback flag regression for multiple clients.

## Risks And Test Signals

Risks include global UGI/security leakage, brittle error-message regexes, environment-dependent Kerberos behavior, timing in postponed-response futures, and hidden connection reuse. Test signals include negotiated `AuthMethod`, connection `saslQop`, server `saslServer` disposal behavior, invalid-token `RemoteException` unwrapping, fallback atomic booleans for first and second clients, PLAIN callback completion, and ordered completion of ten randomly released postponed calls under SASL protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestSaslRPC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestServer.java

## Purpose

`TestServer` covers focused unit behavior in Hadoop IPC `Server`: socket binding with configured ranges, exception logging suppression/terse modes, exception-handler classification, and purge interval configuration.

## Important APIs, Types, And Functions

The file uses `Server.bind(...)`, anonymous `Server` subclasses over `LongWritable`, `Server.logException()`, `Server.ExceptionsHandler`, `addSuppressedLoggingExceptions()`, `addTerseExceptions()`, and `getPurgeIntervalNanos()`. It defines three dummy exception types to test logging classes.

## Control Flow

Binding tests occupy or create sockets, set a `TestRange` configuration, and verify `Server.bind()` picks a free port in range, binds without range, accepts empty range config, or throws `BindException` when the only configured port is occupied. Logging tests construct a server and mocked logger, then assert suppressed exceptions produce no logger calls, terse exceptions log only a message, and other exceptions log with stack trace. Handler tests add multiple exception classes and query classification. The purge test sets `IPC_SERVER_PURGE_INTERVAL_MINUTES_KEY` and compares nanos conversion.

## State And Persistence Behavior

State is local to sockets, a temporary server instance, mock invocation history, and server exception-handler sets. No filesystem persistence is involved. Socket cleanup is handled in `finally` blocks.

## Dependencies And Integration Points

The tests integrate with Java `ServerSocket`, Hadoop `Configuration`, IPC server internals, SLF4J logging, Mockito, and `CommonConfigurationKeysPublic`. They are a direct guard for server bootstrap and operator-facing exception logging behavior.

## Risks And Test Signals

Risks include port allocation races, platform socket semantics, accidental stack-trace logging for terse classes, and unit conversion errors for purge interval. Signals are bound socket assertions, caught `BindException`, zero/mock interaction checks, and exact nanos conversion for the purge interval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestShadedProtobufHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestShadedProtobufHelper.java

## Purpose

`TestShadedProtobufHelper` validates conversion of shaded protobuf `ServiceException` into `IOException` for Hadoop IPC call wrappers. It protects exception causality and behavior around `ShadedProtobufHelper.ipc()`.

## Important APIs, Types, And Functions

The tests use `ShadedProtobufHelper.getRemoteException(ServiceException)`, static `ipc(...)`, `LambdaTestUtils.intercept()`, and `verifyCause()`. Inputs cover `ServiceException` with no cause, with an `IOException` cause, and with a non-IO `NullPointerException` cause.

## Control Flow

Each test constructs a source exception, invokes the helper, and verifies whether the original `IOException` is returned or a wrapping `IOException` contains the expected nested cause chain. The `ipc` wrapper tests throw `ServiceException` from a lambda and assert an `IOException` with expected message/cause emerges.

## State And Persistence Behavior

There is no mutable state beyond exception objects. The important behavior is preserving cause identity where possible and wrapping non-IO causes predictably.

## Dependencies And Integration Points

The file integrates with the shaded protobuf package used by Hadoop, IPC helper code, and Hadoop test utilities. It is a compatibility guard for code that bridges protobuf RPC exceptions into Hadoop's checked-IO exception surface.

## Risks And Test Signals

Risks include losing the original `IOException`, hiding non-IO causes, or changing user-visible messages. Test signals are identity comparison for IO causes, exact nested-cause type verification, and intercepted exception messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestShadedProtobufHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestSocketFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestSocketFactory.java

## Purpose

`TestSocketFactory` validates Hadoop socket factory equality, caching, SOCKS proxy configuration, and basic socket creation behavior for `StandardSocketFactory` and `SocksSocketFactory`.

## Important APIs, Types, And Functions

The test uses `NetUtils.getDefaultSocketFactory()`, `StandardSocketFactory`, `SocksSocketFactory`, `Configuration` key `hadoop.rpc.socket.factory.class.default`, and a local `ServerRunnable` echo server. `DummySocketFactory` subclasses `StandardSocketFactory` to exercise map-key equality.

## Control Flow

`startTestServer()` launches a simple TCP server on an ephemeral port and waits until it is ready. `testSocketFactory()` creates sockets through each overload using `InetAddress` and hostname forms, writes `test\n`, and expects `TEST`. `testProxy()` compares SOCKS factories before and after applying a `hadoop.socks.server` configuration. `@AfterEach` stops the server thread and checks for captured errors.

## State And Persistence Behavior

State is an in-memory server thread with volatile readiness/error flags, a server socket, and a map keyed by socket factories. No disk state is used. Cleanup depends on closing the server socket and joining within the timeout.

## Dependencies And Integration Points

The file integrates with Hadoop `NetUtils`, socket factory implementations, Java sockets, proxy configuration, and `SubjectInheritingThread`. It protects RPC client connection caching behavior where socket factory identity participates in cache keys.

## Risks And Test Signals

Risks include equality/hash changes collapsing distinct factories, hangs in server startup/shutdown, proxy configuration not normalizing factory equality, and socket overload regressions. Signals are map size/removal checks, successful uppercase echo through all create methods, proxy equality assertions, and absence of server-thread errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestSocketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestWeightedRoundRobinMultiplexer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestWeightedRoundRobinMultiplexer.java

## Purpose

`TestWeightedRoundRobinMultiplexer` validates the queue-selection pattern generated by `WeightedRoundRobinMultiplexer`, including invalid construction, default exponential weights, and configured custom weights.

## Important APIs, Types, And Functions

The file instantiates `WeightedRoundRobinMultiplexer(int numQueues, String namespace, Configuration conf)` and repeatedly calls `getAndAdvanceCurrentIndex()`. It uses `IPC_CALLQUEUE_WRRMUX_WEIGHTS_KEY` for namespace-scoped weight configuration.

## Control Flow

Constructor tests assert negative, zero, and mismatched weight counts throw `IllegalArgumentException`, while matching count succeeds. Default-pattern tests check one through four queue cases: one queue always returns zero, two queues produce `0,0,1`, three produce `0,0,0,0,1,1,2`, and four produce `8x0,4x1,2x2,1x3`. Custom-pattern tests configure equal weights and `1,3,2`, then assert repeated cycles.

## State And Persistence Behavior

The multiplexer keeps only in-memory current index/cycle state. Configuration is read at construction and no persistent state is written.

## Dependencies And Integration Points

The test integrates with IPC call queue scheduling and Hadoop `Configuration`. It is a behavior guard for RPC scheduler fairness and priority queue weighting.

## Risks And Test Signals

Risks include namespace normalization mistakes, off-by-one cycle resets, accepting bad queue counts, or custom weights not repeating. Signals are exact index sequences and exception checks for invalid configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestWeightedRoundRobinMultiplexer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestWeightedTimeCostProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestWeightedTimeCostProvider.java

## Purpose

`TestWeightedTimeCostProvider` validates cost calculation for IPC processing details when timing components are weighted. It protects RPC scheduler cost accounting for queue, lock-free, shared-lock, and exclusive-lock timing.

## Important APIs, Types, And Functions

The file uses `WeightedTimeCostProvider`, `ProcessingDetails`, `ProcessingDetails.Timing`, default weight constants, `init(namespace, conf)`, and `getCost(processingDetails)`.

## Control Flow

`setup()` creates a provider and a millisecond-based `ProcessingDetails` with queue, lock-free, lock-shared, and lock-exclusive values. One test asserts `getCost()` before `init()` throws `AssertionError`. The default test initializes empty config and computes cost from default lock weights. The configured test sets namespace-specific weights for queue, lock-free, and lock-shared, includes an unrelated `bar` lock-exclusive key, and asserts only `foo.*` keys apply.

## State And Persistence Behavior

The provider stores initialized weights in memory. `ProcessingDetails` stores timing values by enum in memory; no persistence is involved.

## Dependencies And Integration Points

This tests IPC scheduling cost providers that consume per-call `ProcessingDetails`. It integrates with Hadoop configuration naming under `<namespace>.weighted-cost.*`.

## Risks And Test Signals

Risks include allowing use before initialization, applying wrong namespace weights, ignoring queue weight, or changing default weight behavior. Signals are exact arithmetic expectations and namespace isolation for the unrelated `bar` setting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestWeightedTimeCostProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/metrics/TestDecayRpcSchedulerDetailedMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/metrics/TestDecayRpcSchedulerDetailedMetrics.java

## Purpose

`TestDecayRpcSchedulerDetailedMetrics` ensures `DecayRpcScheduler` registers and unregisters its detailed metrics source with the default metrics system.

## Important APIs, Types, And Functions

The test constructs `DecayRpcScheduler(4, "ipc.8020", conf)`, obtains `scheduler.getDecayRpcSchedulerDetailedMetrics()`, queries `DefaultMetricsSystem.instance().getSource(metrics.getName())`, and calls `scheduler.stop()`.

## Control Flow

After scheduler construction, the detailed metrics source must be visible in the metrics system. After `stop()`, the source must be absent.

## State And Persistence Behavior

State lives in the singleton/default metrics system registry and the scheduler instance. No durable state is written.

## Dependencies And Integration Points

This file integrates IPC scheduler metrics with Hadoop metrics2 `DefaultMetricsSystem`. It is a lifecycle guard for avoiding leaked metrics sources between schedulers/tests.

## Risks And Test Signals

Risks include duplicate/leaked source names, missing registration, or failure to unregister on stop. Signals are `assertNotNull` before stop and `assertNull` after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/metrics/TestDecayRpcSchedulerDetailedMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/metrics/TestRpcMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/metrics/TestRpcMetrics.java

## Purpose

`TestRpcMetrics` verifies that an IPC `Server` registers both aggregate and detailed RPC metrics sources and unregisters them when stopped.

## Important APIs, Types, And Functions

The test creates an anonymous `Server` over `LongWritable`, gets `server.getRpcMetrics()` and `server.getRpcDetailedMetrics()`, queries `DefaultMetricsSystem.instance()`, and calls `server.stop()`.

## Control Flow

The server constructor initializes metrics. The test asserts both metric source names are present, stops the server, then asserts both are absent from the metrics system.

## State And Persistence Behavior

The relevant state is default metrics-system registration for the server lifetime. There is no external persistence.

## Dependencies And Integration Points

It integrates Hadoop IPC server lifecycle with metrics2 source registration and complements scheduler metrics lifecycle tests.

## Risks And Test Signals

Risks include metrics registry leaks, missing detailed metrics, or stop not unregistering sources. Signals are not-null source lookup before stop and null lookup after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/metrics/TestRpcMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/jmx/TestJMXJsonServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/jmx/TestJMXJsonServlet.java

## Purpose

`TestJMXJsonServlet` validates Hadoop's `/jmx` servlet JSON output, query/get parameters, NaN rendering when filtering is disabled, CORS headers, and disallowed HTTP TRACE handling.

## Important APIs, Types, And Functions

The test extends `HttpServerFunctionalTest`, uses `createTestServer()`, `getServerURL()`, `readOutput(URL)`, `JMXJsonServlet.ACCESS_CONTROL_ALLOW_METHODS`, `ACCESS_CONTROL_ALLOW_ORIGIN`, and regex helper `assertReFind()`.

## Control Flow

`@BeforeAll` starts a test `HttpServer2`. `testQuery()` fetches `/jmx?qry=java.lang:type=Runtime`, `/jmx?qry=java.lang:type=Memory`, full `/jmx` output after setting a system property to `Float.NaN`, and `/jmx?get=java.lang:type=Memory::HeapMemoryUsage`. It also checks an invalid get request returns `"ERROR"` and confirms CORS headers. `testTraceRequest()` sends TRACE and expects HTTP 405.

## State And Persistence Behavior

The server runs in-memory on an ephemeral port. The test mutates a JVM system property to expose NaN behavior. No durable state is written.

## Dependencies And Integration Points

This tests `HttpServer2`, the JMX servlet, Java platform MBeans, servlet response codes, and HTTP URL connection behavior. It is an integration surface for Hadoop web UIs exposing JMX JSON.

## Risks And Test Signals

Risks include brittle regexes against JSON formatting, global system-property leakage, servlet method security regressions, and CORS header changes. Signals are regex matches for bean names/modeler type/NaN, invalid get error output, CORS header presence, and 405 for TRACE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/jmx/TestJMXJsonServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/jmx/TestJMXJsonServletNaNFiltered.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/jmx/TestJMXJsonServletNaNFiltered.java

## Purpose

`TestJMXJsonServletNaNFiltered` verifies the `/jmx` servlet replaces NaN values with numeric `0.0` when `JMX_NAN_FILTER` is enabled.

## Important APIs, Types, And Functions

The test uses `Configuration.setBoolean(JMX_NAN_FILTER, true)`, `HttpServerFunctionalTest.createTestServer(configuration)`, `readOutput()`, and regex helper `assertReFind()`.

## Control Flow

The server is started once with NaN filtering enabled. The test sets the system property `THE_TEST_OF_THE_NAN_VALUES` to `Float.NaN`, reads `/jmx`, and asserts the property entry appears with `value` equal to `0.0` rather than the string `"NaN"`.

## State And Persistence Behavior

State is limited to the test HTTP server and JVM system property. There is no persisted state, but the system-property mutation is global to the JVM.

## Dependencies And Integration Points

It integrates Hadoop configuration, `HttpServer2`, `JMXJsonServlet`, and platform MBean system-property exposure. It complements the unfiltered servlet test.

## Risks And Test Signals

Risks include mismatched numeric/string rendering, global property leakage, and JSON formatting sensitivity. The signal is a full servlet request proving filtered NaN values become `0.0` in emitted JSON.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/jmx/TestJMXJsonServletNaNFiltered.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/log/TestLogLevel.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/log/TestLogLevel.java

## Purpose

`TestLogLevel` validates Hadoop's dynamic log-level CLI and servlet over HTTP, HTTPS, and optional SPNEGO. It covers command parsing, server setup with SSL/Kerberos, successful get/set operations, and protocol-mismatch failures.

## Important APIs, Types, And Functions

The class extends `KerberosSecurityTestcase`. It uses `LogLevel.CLI`, `LogLevel.Servlet`, `HttpServer2.Builder`, `KeyStoreTestUtil`, `KerberosTestUtils`, `AuthenticationFilterInitializer`, `AccessControlList`, and `GenericTestUtils.setLogLevel()`. Helpers include `validateCommand()`, `createServer(protocol,isSpnego)`, `testDynamicLogLevel()`, `getLevel()`, and `setLevel()`.

## Control Flow

`@BeforeAll` creates a randomized base directory and SSL config. `@BeforeEach` creates client/server principals in the mini KDC. Command tests parse valid and invalid argument combinations without contacting a server. Dynamic tests configure optional SPNEGO, build an HTTP or HTTPS server on an ephemeral port, optionally install the log-level servlet with auth, run CLI get and set under client Kerberos identity, assert the logger's effective level changes, stop the server, and restore the old level. Mismatch tests intentionally connect HTTPS to HTTP or HTTP to HTTPS and assert SSL/socket exceptions contain expected authentication endpoint messages.

## State And Persistence Behavior

State includes temporary keystore/truststore files under the randomized base directory, mini-KDC principals/keytab, static Hadoop configurations, global UGI configuration during SPNEGO tests, and the actual log4j logger level. Teardown cleans SSL config and deletes the base directory.

## Dependencies And Integration Points

This file integrates Hadoop HTTP server, log-level servlet/CLI, SSL configuration, Kerberos/SPNEGO auth filters, ACLs, UGI, log4j, and Hadoop test KDC infrastructure. It is an end-to-end test for operator-facing runtime log-level changes.

## Risks And Test Signals

Risks include slow/flaky Kerberos setup, port/protocol mismatch differences across JDKs, global auth/log level leakage, and brittle exception text. Signals include command parser boolean outcomes, successful CLI get/set over authenticated/unauthenticated HTTP(S), exact logger effective-level assertions, and expected failures for protocol mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/log/TestLogLevel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/log/TestLogThrottlingHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/log/TestLogThrottlingHelper.java

## Purpose

`TestLogThrottlingHelper` validates time-based log suppression and aggregated statistics emitted by `LogThrottlingHelper`, including named loggers and primary/dependent logger coordination.

## Important APIs, Types, And Functions

The tests use `LogThrottlingHelper`, `LogThrottlingHelper.LogAction`, `FakeTimer`, `record(...)`, `record(name,time,values...)`, `shouldLog()`, `getCount()`, `getStats(index)`, and `getCurrentStats(name,index)`.

## Control Flow

Each test advances a fake timer rather than sleeping. Basic tests assert an initial log is allowed, intermediate calls are suppressed, and a call after the period logs. Value tests feed numeric values during suppressed intervals and assert the next allowed action reports count, mean, max, and min. Named logger tests verify independent loggers when no primary is configured and dependent loggers that only log after primary activation when a primary name is set.

## State And Persistence Behavior

State is in-memory per-helper timing and rolling stats keyed by optional logger names. `FakeTimer` makes time deterministic. No external state is used.

## Dependencies And Integration Points

The test integrates with Hadoop's logging helper and utility fake timer. Runtime users depend on this helper to reduce repetitive logs while retaining aggregate signal.

## Risks And Test Signals

Risks include value-count mismatch handling, primary/dependent coordination bugs, losing suppressed-call statistics, and off-by-one period boundaries. Signals are deterministic `shouldLog` assertions, stats mean/min/max checks, illegal-argument assertion for inconsistent value arity, and current-stat lookups for named loggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/log/TestLogThrottlingHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/filter/TestPatternFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/filter/TestPatternFilter.java

## Purpose

`TestPatternFilter` validates common include/exclude semantics shared by metrics glob and regex filters for names, tags, and complete metrics records.

## Important APIs, Types, And Functions

The file uses `GlobFilter`, `RegexFilter`, `MetricsFilter.accepts(...)`, `ConfigBuilder`, `SubsetConfiguration`, `MetricsTag`, and mocked `MetricsRecord`. Public helpers `newGlobFilter()` and `newRegexFilter()` are reused by other metrics tests.

## Control Flow

Tests build filter configs with `include`, `include.tags`, `exclude`, and `exclude.tags`, then call helper assertions against strings, tag lists, and mock records. Cases cover empty config accepting everything, include-only whitelisting, exclude-only blacklisting, combined include/exclude accepting unmatched items while rejecting excluded matches, and include patterns overriding identical excludes. Per-tag assertions ensure list-level acceptance and individual tag decisions line up for both glob and regex filters.

## State And Persistence Behavior

State is only in the constructed `PropertiesConfiguration`/`SubsetConfiguration` and initialized filter objects. No persistence is involved.

## Dependencies And Integration Points

The test integrates with metrics2 filter implementations, config utilities, interned metric tags, and Mockito. Other tests import its filter factory helpers for collector filtering.

## Risks And Test Signals

Risks include glob/regex semantic divergence, wrong precedence between include and exclude, rejecting unmatched items when both filters are configured, and incorrect tag-list aggregation. Signals compare both filter types on every case and assert both aggregate list result and individual tag result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/filter/TestPatternFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/ConfigBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/ConfigBuilder.java

## Purpose

`ConfigBuilder` is a test helper for constructing Apache Commons `PropertiesConfiguration` instances fluently and saving them to metrics2 config files.

## Important APIs, Types, And Functions

The class exposes public final `config`, constructor initialization with `DefaultListDelimiterHandler(',')`, `add(String,Object)`, `save(String)`, and `subset(String)`.

## Control Flow

Tests create a builder, chain `add()` calls to append properties, optionally call `save()` to write a properties file, or call `subset(prefix)` to return a `SubsetConfiguration` with `.` delimiter. `save()` wraps any write failure in `RuntimeException`.

## State And Persistence Behavior

State is the mutable `PropertiesConfiguration`. `save()` persists the configuration to a filename with `FileWriter`; callers are responsible for target directories and cleanup. The list delimiter makes comma-separated values split consistently in metrics config tests.

## Dependencies And Integration Points

It integrates with Commons Configuration and is used across metrics tests for filters, metrics-system setup, Ganglia sinks, and config parsing.

## Risks And Test Signals

Risks include unclosed writer behavior, target-file collisions in shared test classpaths, and delimiter changes affecting list-valued tests. It is itself a helper, so signals come from dependent tests successfully loading saved configs and subset views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/ConfigBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/ConfigUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/ConfigUtil.java

## Purpose

`ConfigUtil` is a package-private metrics2 test utility for dumping Commons configurations and asserting two configurations contain exactly the same keys and values.

## Important APIs, Types, And Functions

It provides `dump(Configuration)`, `dump(String, Configuration)`, `dump(String, Configuration, PrintWriter)`, and `assertEq(Configuration expected, Configuration actual)`.

## Control Flow

`dump()` copies the input into a `PropertiesConfiguration`, optionally prints a header, and writes it to the supplied writer. `assertEq()` iterates expected keys to assert presence/value equality in actual, then iterates actual keys to reject extras.

## State And Persistence Behavior

The utility has no persistent state. `dump()` writes to a `PrintWriter` provided by caller or `System.out`; `assertEq()` only reads configurations.

## Dependencies And Integration Points

It integrates with Commons Configuration and JUnit assertions. `TestMetricsConfig` uses `assertEq()` to validate merged and instance-specific metrics configuration behavior.

## Risks And Test Signals

Risks include value equality differences for list-valued properties and iterator ordering assumptions for debug output. Signals are precise missing-key, mismatched-value, and extra-key assertions in config tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/ConfigUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/MetricsLists.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/MetricsLists.java

## Purpose

`MetricsLists` is a tiny package-private helper that creates metrics lists for tests through the real `MetricsCollectorImpl`/`MetricsRecordBuilderImpl` path.

## Important APIs, Types, And Functions

It exposes `static MetricsRecordBuilderImpl builder(String name)`, which returns `new MetricsCollectorImpl().addRecord(name)`.

## Control Flow

Callers obtain a record builder, add counters/gauges through normal builder APIs, and then read `.metrics()` from the builder. This avoids hand-constructing metric implementation lists.

## State And Persistence Behavior

All state is in the newly allocated collector and builder. There is no persistence or static cache.

## Dependencies And Integration Points

The helper is used by tests such as `TestMetricsSystemImpl` and `TestMetricsVisitor` to construct expected metric lists with the same concrete metric classes as production code.

## Risks And Test Signals

The risk is small but important: if builder behavior changes, expected metric construction changes with it and may hide some regressions. Its signal value is consistency with production builder output for equality/visitor tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/MetricsLists.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/MetricsRecords.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/MetricsRecords.java

## Purpose

`MetricsRecords` is a public test utility for asserting tags and metric values in a `MetricsRecord` by name.

## Important APIs, Types, And Functions

It provides `assertTag(record, tagName, expectedValue)`, `assertMetric(record, metricName, expectedValue)`, `getMetricValueByName(record, metricName)`, and `assertMetricNotNull(record, metricName)`. Private predicates match `MetricsTag.name()` and `AbstractMetric.name()`.

## Control Flow

Each assertion method searches the record's tags or metrics for the first matching name, asserts it is not null, and compares or returns the value. Metrics are streamed from the iterable with `StreamSupport`.

## State And Persistence Behavior

The utility is stateless and reads only supplied records. It handles null tag/metric iterables by returning null from the private lookup, causing the public assertion to fail.

## Dependencies And Integration Points

It integrates with metrics2 `MetricsRecord`, `MetricsTag`, `AbstractMetric`, and JUnit assertions. It is designed for tests outside the `impl` package that need concise metric lookups.

## Risks And Test Signals

Risks include first-match ambiguity when duplicate names exist and strict numeric type equality. Test signals are targeted assertion failures that name missing metrics and exact expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/MetricsRecords.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestGangliaMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestGangliaMetrics.java

## Purpose

`TestGangliaMetrics` validates metrics2 Ganglia sink prefix tagging and emitted datagram records for Ganglia 3.0 and 3.1 sinks.

## Important APIs, Types, And Functions

The file uses `GangliaSink30`, `GangliaSink31`, `AbstractGangliaSink`, `GangliaMetricsTestHelper.setDatagramSocket()`, `MetricsSystemImpl`, annotated `TestSource`, and a custom `MockDatagramSocket` that captures sent bytes.

## Control Flow

`testTagsForPrefix()` configures `tagsForPrefix` for contexts `all`, `some`, and `none`, builds a `MetricsRecordImpl`, and asserts appended prefixes include all, selected, or no tags. `testGangliaMetrics2()` writes metrics config, starts a metrics system, registers a source and two Ganglia sinks with mock sockets, publishes metrics manually, stops the system, and checks captured datagrams contain expected metric names. Ganglia 3.1 expects twice as many packets because it emits metadata plus value records.

## State And Persistence Behavior

State includes a saved test metrics properties file, metrics system registration, source counter/gauge/rate values, and captured datagram byte arrays. `MockDatagramSocket` copies packet bytes to avoid reuse aliasing.

## Dependencies And Integration Points

This integrates metrics2 core, annotation-based sources, Ganglia sink implementations, UDP datagram sending, and test helper reflection into sink socket state.

## Risks And Test Signals

Risks include UDP packet format changes, prefix tag ordering, datagram buffer reuse, config-file race with other tests, and manual publish timing. Signals are exact prefix strings, expected metric-name coverage, and expected datagram counts for Ganglia 3.0 versus 3.1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestGangliaMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsCollectorImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsCollectorImpl.java

## Purpose

`TestMetricsCollectorImpl` validates metrics collector filtering at record and per-metric levels.

## Important APIs, Types, And Functions

The tests use `MetricsCollectorImpl`, `MetricsRecordBuilderImpl`, `setRecordFilter()`, `setMetricFilter()`, `ConfigBuilder`, and filter factory helpers from `TestPatternFilter`.

## Control Flow

`recordBuilderShouldNoOpIfFiltered()` configures a record exclude filter for `foo`, adds a record named `foo`, tries to add a tag and gauge, and asserts the builder has no tags, no metrics, no record, and the collector has no records. `testPerMetricFiltering()` sets a metric exclude filter for `foo`, adds a tag, a counter `c0`, and a gauge `foo`, then asserts only the tag and counter remain.

## State And Persistence Behavior

State is in the collector, builder, and filter objects. No persistence is involved.

## Dependencies And Integration Points

It integrates metrics2 collector/builder internals with glob filter semantics. It depends on `TestPatternFilter` helpers for consistent filter initialization.

## Risks And Test Signals

Risks include filtered record builders accidentally retaining data, metric filters applying to tags, or filtered metrics still appearing in records. Signals are exact tag/metric list sizes, null record assertion, and collector record count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsCollectorImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsConfig.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsConfig.java

## Purpose

`TestMetricsConfig` validates metrics2 configuration loading, prefix scoping, wildcard defaults, instance extraction, missing-file behavior, load order, and comma-delimited values.

## Important APIs, Types, And Functions

The file uses `MetricsConfig.create(prefix, filenames...)`, `getInstanceConfigs(type)`, `ConfigBuilder`, `ConfigUtil.assertEq()`, and `getTestFilename(basename)`.

## Control Flow

`testCommon()` writes a properties file containing global defaults, prefix defaults, type defaults, and instance-specific values, creates a `MetricsConfig` for `p1`, asserts the scoped config, and delegates to `testInstances()`. Instance tests verify map sizes and default lookup fallbacks. Other tests assert missing files return an empty config, prefix-named default files load when available, explicit file load order works, and comma-delimited values become multiple properties.

## State And Persistence Behavior

The tests write `.properties` files under `test.build.classes` or `target/test-classes`. Configuration state is loaded from those files and in-memory Commons Configuration objects.

## Dependencies And Integration Points

It integrates Commons Configuration, Hadoop metrics2 config parsing, test config builder/utilities, and the classpath/test-build output directory convention used by metrics system tests.

## Risks And Test Signals

Risks include file collisions, wildcard/default precedence regressions, list delimiter changes, and accidentally treating missing files as fatal. Signals are exact scoped config equality, instance map counts, default lookup assertions, and split value equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsSourceAdapter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsSourceAdapter.java

## Purpose

`TestMetricsSourceAdapter` validates metrics source adaptation for metrics collection and JMX exposure, including stale metric purging and a race around JMX cache refresh.

## Important APIs, Types, And Functions

The tests construct `MetricsSourceAdapter`, annotation-backed `MetricsSource`s via `MetricsAnnotations.newSourceBuilder()`, inspect `MBeanInfo`/`MBeanAttributeInfo`, call `getMetrics()`, `getAttribute()`, and use scheduled `SourceUpdater` and `SourceReader` helpers. `PurgableSource`, `TestSource`, and `TestMetricsSource` provide controlled metric changes.

## Control Flow

`testPurgeOldMetrics()` uses a source that emits a new key name each collection and asserts the latest key remains exported after the JMX cache TTL. `testGetMetricsAndJmx()` verifies initial metric value zero through collector and JMX, increments the counter, then verifies both paths see the update. `testMetricCacheUpdateRace()` runs one scheduled task that resets adapter records and another that reads JMX attributes and mutates the source key every two TTLs for ten seconds, asserting no missing-key error occurs.

## State And Persistence Behavior

State includes adapter JMX cache (`lastRecs` behavior), source counters/key-value pairs, scheduled executor tasks, and an `AtomicBoolean` error flag. There is no durable persistence. Threads are shut down after the race test.

## Dependencies And Integration Points

This integrates metrics annotations, metrics source builder, JMX MBean exposure, metrics collector implementation, Guava thread factory, Java scheduled executors, and log4j. It directly guards Hadoop JMX metrics visibility.

## Risks And Test Signals

Risks include timing flakiness from sleeps and ten-second race window, stale JMX attributes, dropped dynamic metrics, and executor cleanup issues. Signals are MBean attribute-name presence, exact JMX attribute values before/after increment, and the race test's `hasError` flag staying false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsSourceAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsSystemImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsSystemImpl.java

## Purpose

`TestMetricsSystemImpl` is the main metrics2 system integration test. It covers startup/shutdown, source and sink registration, filters, concurrent publishing, hanging sinks, queue sizing, unregister/restart behavior, JMX cache TTL, multiple sink periods, and metrics-system restart.

## Important APIs, Types, And Functions

The class uses `MetricsSystemImpl`, `DefaultMetricsSystem`, `MetricsSink`, `MetricsSource`, `MetricsRegistry`, mutable metrics annotations, `ConfigBuilder`, `MetricsConfig`, sink/source adapters, and Mockito captors. Helper classes include `TestSink`, `CollectingSink`, `HangingSink`, `TestClosableSink`, `TestSource`, and `TestSource2`.

## Control Flow

Initialization tests write metrics config with source/metric filters, start a metrics system, register sources/sinks, publish, stop/shutdown, and assert captured records match expected filtered metrics. The multithreaded test registers ten sources and uses barriers so all threads set gauges and publish simultaneously, then asserts every source's metric is collected and no dropped publications occur. Hanging/closeable sink tests verify dropped publish counters, interruption on stop, later sink calls, and stop behavior when `putMetrics()` loops until closed. Other tests validate duplicate registration semantics before/after start, unregistering sources, default names for unnamed source registration, queue size metrics for slow sinks, JMX cache TTL defaults, multiple sink periods on timer events, and sink adapter preservation after restart.

## State And Persistence Behavior

The file writes test metrics config files, mutates the singleton default metrics system into mini-cluster mode, maintains source/sink registries, sink queues, dropped-publish counters, MBean names, and background sink threads. Tests usually stop and shutdown systems in `finally` blocks, but global metrics system state is a cross-test concern.

## Dependencies And Integration Points

It integrates metrics2 core implementation, annotations, mutable metric classes, source/sink adapters, filters, config parsing, JMX registration, concurrency primitives, Mockito, and Hadoop test utilities. It is the broadest signal for metrics system behavior across source collection and sink publication.

## Risks And Test Signals

Risks include timing flakes in async sink delivery, leaked threads or MBeans, global default metrics contamination, queue capacity/dropped counter regressions, and race conditions during concurrent publish. Signals include captured record equality, expected context/hostname tags, expected metric lists, dropped counter assertions, sink call timeouts, queue size metric extraction, source adapter lookup after restart, and wait-for checks for multiple sink periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsSystemImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsVisitor.java

## Purpose

`TestMetricsVisitor` validates dispatch from concrete `AbstractMetric` types to the correct `MetricsVisitor.counter()` or `MetricsVisitor.gauge()` overloads.

## Important APIs, Types, And Functions

The test uses `MetricsVisitor`, `AbstractMetric.visit(visitor)`, `MetricsLists.builder()`, `Interns.info()`, Mockito `ArgumentCaptor<MetricsInfo>`, and verification of int, long, float, and double values.

## Control Flow

The test builds a metric list with int/long counters and int/long/float/double gauges, visits each metric with a mock visitor, then verifies each expected visitor method was called with the correct metric info and value.

## State And Persistence Behavior

State is only the generated metric list and Mockito captured arguments. There is no persistent or global state.

## Dependencies And Integration Points

It integrates metric implementation classes, visitor interface dispatch, interned metric metadata, and the metrics list helper. Downstream sinks and serializers rely on the same visitor dispatch.

## Risks And Test Signals

Risks include numeric overload mismatches, counters treated as gauges, and lost metric descriptions. Signals are per-overload Mockito verifications and captured `MetricsInfo` name/description checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestSinkQueue.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestSinkQueue.java

## Purpose

`TestSinkQueue` validates the half-blocking queue used by metrics sinks. It covers enqueue/dequeue behavior, blocking on empty queues, dropping on full queues, consume-all, exception consistency, clearing, hanging consumers, and illegal concurrent consumers.

## Important APIs, Types, And Functions

The file uses `SinkQueue<T>`, `enqueue()`, `dequeue()`, `consume()`, `consumeAll()`, `front()`, `back()`, `size()`, `capacity()`, `clear()`, `SinkQueue.Consumer`, and test helper `newSleepingConsumerQueue()`.

## Control Flow

Basic tests enqueue and consume integers while checking front/back/size. Empty tests start a consumer thread blocked in `dequeue()` and `consume()` then enqueue values to release it. Full tests assert nonblocking drops when capacity is exceeded. `testConsumerException()` ensures a thrown consumer exception leaves the queue consistent. Hanging-consumer tests run a daemon consumer that sleeps for a long time, then assert producers do not block and queue state is preserved. Concurrent consumer tests assert `ConcurrentModificationException` for clear, consume, consumeAll, and dequeue while another consumer is active.

## State And Persistence Behavior

State is in-memory queue contents, active-consumer tracking, and test threads/latches. There is no persistence. Sleeping consumer threads are daemon threads to avoid blocking JVM exit.

## Dependencies And Integration Points

It integrates with the metrics sink queue implementation and `SubjectInheritingThread`. Metrics system sink adapters depend on these semantics for nonblocking publication and safe backpressure.

## Risks And Test Signals

Risks include producer blocking under full queues, corrupted queue state after consumer exceptions, deadlocks on empty queues, and concurrent consumers violating invariants. Signals are exact queue contents/size/front/back assertions, mock callback counts, dropped enqueue false returns, and expected `ConcurrentModificationException`s.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestSinkQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/MetricsTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/MetricsTestHelper.java

## Purpose

`MetricsTestHelper` exposes package-private metrics behavior to tests, specifically replacing the scheduled rolling window task in `MutableRollingAverages`.

## Important APIs, Types, And Functions

The class is `final` with a private constructor, a logger, and static `replaceRollingAveragesScheduler(MutableRollingAverages, int numWindows, long interval, TimeUnit)`, which delegates to `mutableRollingAverages.replaceScheduledTask(...)`.

## Control Flow

Tests call the helper with a mutable rolling-averages metric and desired window parameters. The helper performs no validation and directly invokes the package-private method.

## State And Persistence Behavior

State changes occur inside the supplied `MutableRollingAverages`, replacing its scheduler/task configuration. No state is stored in the helper and no persistence is written.

## Dependencies And Integration Points

It integrates with `MutableRollingAverages` and Java `TimeUnit`. It is a test-only bridge around encapsulation for metrics rolling average timing.

## Risks And Test Signals

Risks include misuse with invalid window/interval values and hidden scheduler resource leaks in callers. Signals come from downstream rolling-average tests that can deterministically shrink scheduling windows through this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/MetricsTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestInterns.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestInterns.java

## Purpose

`TestInterns` validates interning and bounded cache eviction for metrics metadata (`MetricsInfo`) and tags (`MetricsTag`).

## Important APIs, Types, And Functions

The tests use `Interns.info()`, `Interns.tag()`, cache-size constants `MAX_INFO_NAMES`, `MAX_INFO_DESCS`, `MAX_TAG_NAMES`, and `MAX_TAG_VALUES`, plus `assertSame`/`assertNotSame`.

## Control Flow

Basic tests assert identical name/description or tag triples return the same object. Overflow tests create more distinct names or values than the configured maximum and assert an early object remains interned until the limit is crossed, then is no longer the same object.

## State And Persistence Behavior

The relevant state is global/static intern caches inside `Interns`. No disk state exists. Because caches are global, test order and prior cache population can influence exact eviction behavior if not isolated.

## Dependencies And Integration Points

It integrates with metrics2 metadata construction used throughout collectors, registries, and sinks. Interning reduces object churn and supports fast identity/equality paths.

## Risks And Test Signals

Risks include unbounded cache growth, premature eviction, or failure to preserve object identity for repeated metadata. Signals are object identity assertions before and after cache overflow thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestInterns.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMetricsAnnotations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMetricsAnnotations.java

## Purpose

`TestMetricsAnnotations` validates annotation-driven metrics source construction for fields, methods, class-level metadata, hybrid `MetricsSource` implementations, and invalid annotated shapes.

## Important APIs, Types, And Functions

The file uses `MetricsAnnotations.makeSource()`, `@Metrics`, `@Metric`, mutable metric types (`MutableCounterInt`, `MutableGaugeLong`, `MutableRate`, etc.), `MetricsSource`, `MetricsCollector`, `MetricsRecordBuilder`, `MetricsException`, and `MetricsAsserts.getMetrics()`.

## Control Flow

Field tests create a class with annotated mutable counters/gauges/rates/stats, mutate values, snapshot through the generated source, and verify builder calls. Method tests expose numeric gauges, counters, and tags through annotated getters. Class tests verify `@Metrics(about,context)` controls record info/context. Hybrid tests wrap a class that already implements `MetricsSource` plus annotated registry fields, asserting both manual records and annotation-derived metrics appear. Negative tests assert bad field types, methods with arguments, unsupported return types, bad hybrid definitions, and empty metrics classes throw exceptions.

## State And Persistence Behavior

State is held in mutable metric fields and generated source wrappers. There is no persistence. Hybrid sources may write multiple records per snapshot and use an embedded `MetricsRegistry`.

## Dependencies And Integration Points

This is a central integration test for metrics annotations, mutable metric classes, interned metadata, collector/builder interactions, and error validation. Many Hadoop components depend on annotation-based metrics source creation.

## Risks And Test Signals

Risks include incorrect metric name derivation, wrong counter/gauge type mapping, accepting invalid annotations, duplicate record creation in hybrids, or losing class context. Signals are Mockito verifications of exact builder calls, `assertSame` for hybrid source identity, and exception assertions for invalid definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMetricsAnnotations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMetricsRegistry.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMetricsRegistry.java

## Purpose

`TestMetricsRegistry` validates `MetricsRegistry` factory methods, duplicate metric rejection, illegal metric-name validation, add-by-name stat behavior, and invalid quantile interval handling.

## Important APIs, Types, And Functions

The tests use `MetricsRegistry`, `newCounter()`, `newGauge()`, `newStat()`, `newQuantiles()`, `get()`, `metrics()`, `add(name,value)`, `MutableCounter*`, `MutableGauge*`, `MutableStat`, `MetricsException`, and mocked `MetricsRecordBuilder`.

## Control Flow

`testNewMetrics()` creates counters, gauges, and a stat, checks registry size and concrete metric classes, then expects duplicate counter creation to fail. `testMetricsRegistryIllegalMetricNames()` seeds valid metrics and tries names with spaces, trailing spaces, leading spaces, tab, and newline, asserting they fail and do not grow the registry. `testAddByName()` auto-creates a stat via `add("s1",42)`, snapshots it, and verifies num-ops/average metrics, then asserts `add()` is unsupported for existing counter/gauge names. `testAddIllegalParameters()` asserts negative quantile intervals are rejected.

## State And Persistence Behavior

State is the in-memory registry map and mutable metric contents. There is no persistence. The helper `expectMetricsException()` is annotated `@Disabled` despite being private, but it is directly invoked by tests and still runs as a helper.

## Dependencies And Integration Points

It integrates metrics registry internals, mutable metric implementations, quantile validation, interned metadata, and metrics assertion utilities. Registry behavior is foundational for annotation and source tests.

## Risks And Test Signals

Risks include allowing duplicate names, accepting whitespace names that break sinks, unsupported `add()` paths mutating wrong metric types, and accepting invalid quantile intervals. Signals are registry size/class assertions, exception message prefixes, and builder verifications for generated stat metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMetricsRegistry.java -->

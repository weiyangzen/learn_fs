<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Server.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Server.java

## Purpose
`Server` is Hadoop Common's abstract IPC server runtime. It owns socket accept/read/write loops, Hadoop RPC framing, SASL authentication, connection-context authorization, request deserialization, call queueing, handler-thread invocation, response serialization, metrics, and lifecycle management. Concrete RPC engines subclass it and implement `call(RPC.RpcKind, String, Writable, long)`.

## Important APIs, Types, And Functions
- Static protocol-engine registry: `registerProtocolEngine`, `getRpcRequestWrapper`, and `getRpcInvoker` map `RPC.RpcKind` values to request wrapper classes and server invokers.
- Static call context accessors: `get()`, `getCurCall()`, `getCallId()`, `getCallRetryCount()`, `getRemoteIp()`, `getRemotePort()`, `getRemoteUser()`, `getProtocol()`, `getPriorityLevel()`, `getClientId()`, and `getAuxiliaryPortEstablishedQOP()` expose per-handler `ThreadLocal` state.
- `Call` is the generic schedulable unit with timing details, retry/client IDs, caller context, authorization header, priority, alignment state, deferred/postponed-response controls, and default no-op execution.
- `RpcCall` extends `Call` with a `Connection`, decoded `Writable` request, response buffer, response parameters, synchronous/deferred response setup, and exception-to-RPC-status mapping.
- `Listener` accepts nonblocking `SocketChannel`s, distributes them to `Reader` threads, and starts/stops the idle scanner.
- `Connection` reads HRPC headers, negotiates auth, parses framed RPC packets, authorizes the connection context, unwraps SASL packets, and queues valid calls.
- `Responder` performs nonblocking response writes, SASL wrapping, selector registration for partial writes, and purges responses stuck longer than `purgeIntervalNanos`.
- `Handler` takes calls from `CallQueueManager`, establishes thread-local call/caller/authorization context, optionally executes under remote UGI, invokes `Call.run()`, and records metrics.
- Configuration helpers choose call queue, scheduler, client backoff, reader counts, maximum data/response sizes, slow-RPC thresholds, and port-specific overrides.
- Lifecycle APIs include constructors, `start()`, `stop()`, `join()`, `addAuxiliaryListener()`, `refreshCallQueue()`, service ACL refreshers, metrics getters, and connection/queue counters.

## Control Flow
Construction binds the primary `Listener`, initializes `CallQueueManager`, authentication methods, SASL properties, metrics sources, a `Responder`, and a scheduled metrics updater. `start()` launches responder, listeners, auxiliary listeners, and handler threads.

The listener accepts sockets, configures TCP options, registers a `Connection` with `ConnectionManager`, and hands it to a reader. A reader calls `Connection.readAndProcess()` whenever the socket is readable. The connection first reads the HRPC magic/version/service/auth bytes, rejects HTTP GETs with a friendly 404 string, sends old-version fatal responses when needed, and sets `AuthProtocol`. It then reads length-prefixed RPC packets, enforces `maxDataLength`, and dispatches each packet to `processOneRpc`.

Out-of-band call IDs handle connection context, SASL negotiation, and pings. SASL negotiation advertises enabled methods, can accelerate token auth with an initial challenge, creates a `SaslServer`, retries once after Kerberos relogin if login state failed, records audit/metrics success or failure, and enables wrapping for QoP values other than `auth`. Connection context parsing establishes the protocol, UGI/proxy UGI, service authorization, and per-user connection counts.

Normal RPC packets validate operation/kind, reject deprecated `RPC_WRITABLE`, reject unregistered protocol kinds before deserializing request payloads, instantiate the registered wrapper, continue tracing if headers contain trace info, build caller context and authorization header, apply optional `AlignmentContext` coordination state, compute priority, and enqueue the `RpcCall`. Handler threads take calls, delay coordinated calls whose client state is ahead of the server, execute the call under the remote UGI when present, then send responses unless deferred. Responses are serialized as protobuf-delimited messages when possible, as writable buffers otherwise, optionally SASL-wrapped, queued to the responder, and written synchronously or through the write selector for partial writes.

## State And Persistence
Runtime state is in memory only: listener/responder/handler threads, selectors, socket channels, response queues, SASL server contexts, connection sets, user connection counters, queue/scheduler state, protocol class cache, RPC kind registry, and metrics objects. No durable data is written by this class. Persistent external effects are network replies, audit/application logs, and metrics exported through Hadoop metrics/JMX. Thread locals (`SERVER`, `CurCall`) are cleared after handler execution; caller and authorization context are also reset around request queueing/execution paths.

## Dependencies And Integration Points
`Server` integrates with `Client`, `RPC.Server`, `RpcInvoker`, `RpcWritable`, protobuf RPC headers, `ProtobufRpcEngine2`, `CallQueueManager`, `RpcScheduler`, `FairCallQueue`, `DecayRpcScheduler`, `RpcMetrics`, `RpcDetailedMetrics`, `ProcessingDetails`, `AlignmentContext`, Hadoop security (`UserGroupInformation`, `SaslRpcServer`, `SecretManager`, `ProxyUsers`, `ServiceAuthorizationManager`), tracing, `NetUtils`, and Hadoop configuration keys. Concrete services plug in through `call(...)`, protocol registration, secret managers, policy providers, and queue/scheduler configuration.

## Risks And Edge Cases
This file is high-risk concurrency and security code. Selector registration races are controlled with queues and `pending`, but close paths may race across reader, responder, listener, and idle scanner. Incorrect response-wait handling can double-send, skip metrics, or leak calls. SASL state transitions must preserve ordering: wrapping is enabled only after the final auth response is sent, and SIMPLE fallback must be consistent with advertised methods. Request deserialization is intentionally delayed until registered protocol kinds are verified; changing that path can reintroduce untrusted deserialization exposure. Queue overflow maps to client backoff and sometimes disconnects, so scheduler exceptions must carry the right RPC status. `AlignmentContext` requeueing can reorder calls by design. Metrics time-unit conversion and slow-RPC sigma logic depend on enough samples and last-stat snapshots. `ConnectionManager` user counts are incremented only after authorized context and decremented only for established users; missing one path skews JMX. `MetricsUpdateRunner` divides by `TimeUnit.MILLISECONDS.toSeconds(...)`, so very small intervals would be dangerous if configured below one second.

## Test Signals
Relevant tests should cover IPC protocol version mismatch, HTTP-to-IPC response, SASL SIMPLE/Kerberos/TOKEN negotiation, auth failure audit/metrics, proxy-user authorization, unregistered RPC kind rejection, call queue overflow/backoff, deferred/postponed responses, large response warning and buffer reset, SASL wrap/unwrap with auth-int/auth-priv, auxiliary listener QoP reporting, slow-RPC metrics, alignment-context requeueing, idle connection cleanup, refreshCallQueue swaps, and lifecycle shutdown/unregister behavior. Existing Hadoop RPC/security/metrics tests are the natural signal for regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Server.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/StandbyException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/StandbyException.java

## Purpose
`StandbyException` is an evolving `IOException` used when a contacted server is alive but not currently active in an HA group.

## Important APIs, Types, And Functions
- `public class StandbyException extends IOException`.
- `serialVersionUID` is fixed.
- Constructor `StandbyException(String msg)` stores the diagnostic message.

## Control Flow
There is no internal control flow beyond exception construction. Server-side code can throw or tunnel it, and `Server.Connection.getTrueCause` explicitly unwraps this type so clients see standby semantics instead of a generic wrapper.

## State And Persistence
State is the normal throwable message/cause stack held in memory and serialized through RPC exception handling when returned remotely.

## Dependencies And Integration Points
Used by HA-aware services and retry/failover logic. `Server` treats it as terse-log by default and as a true cause during SASL/token error unwrapping.

## Risks And Edge Cases
Changing the type hierarchy would affect failover policies that distinguish standby from other IO failures. Overly broad wrapping can hide this exception unless unwrapped.

## Test Signals
HA failover tests should verify standby responses are propagated to clients and logged tersely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/StandbyException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UnexpectedServerException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UnexpectedServerException.java

## Purpose
`UnexpectedServerException` represents an undeclared exception thrown by an RPC service implementation and surfaced through Hadoop IPC as an `RpcException`.

## Important APIs, Types, And Functions
- Package-visible constructors accept a message or message plus cause.
- Inherits RPC exception behavior from `RpcException`.

## Control Flow
This is a data-bearing exception class. Creation is controlled by IPC exception translation code outside this file.

## State And Persistence
Stores message and optional cause in memory; may be serialized through Hadoop RPC exception handling.

## Dependencies And Integration Points
Depends on `RpcException` and integrates with RPC client/server exception translation for unexpected service-side failures.

## Risks And Edge Cases
Constructors are package-private, so public construction is intentionally constrained to IPC internals. Changing visibility or inheritance can alter client-visible exception compatibility.

## Test Signals
RPC tests that invoke service methods throwing undeclared runtime or checked exceptions should observe the expected wrapped exception type and cause.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UnexpectedServerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UserIdentityProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UserIdentityProvider.java

## Purpose
`UserIdentityProvider` groups schedulable RPC calls by the caller's short user name, allowing scheduler/decay logic to aggregate all jobs from a user.

## Important APIs, Types, And Functions
- Implements `IdentityProvider`.
- `makeIdentity(Schedulable obj)` returns `obj.getUserGroupInformation().getShortUserName()` or `null` when no UGI is present.

## Control Flow
The provider fetches the `UserGroupInformation` from the `Schedulable`. A null UGI produces no identity; otherwise the short user name is returned.

## State And Persistence
Stateless; no fields and no persistent side effects.

## Dependencies And Integration Points
Used by RPC scheduling/fairness components such as decay schedulers and call queues that need an identity key. Depends on `Schedulable` and Hadoop security UGI.

## Risks And Edge Cases
Null identity must be handled by downstream scheduler code. Short-name mapping can collapse Kerberos principals or proxy identities depending on UGI configuration.

## Test Signals
Scheduler tests should cover null UGI, simple users, Kerberos principals mapped to short names, and proxy-user calls if identity semantics matter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UserIdentityProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/VersionedProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/VersionedProtocol.java

## Purpose
`VersionedProtocol` is the legacy/common base interface for Hadoop RPC protocols that support version and method-signature negotiation.

## Important APIs, Types, And Functions
- `getProtocolVersion(String protocol, long clientVersion)` returns the server version for a protocol.
- `getProtocolSignature(String protocol, long clientVersion, int clientMethodsHash)` returns a `ProtocolSignature` including version and supported method data.
- Implementing protocol interfaces are expected to expose a static `versionID`.

## Control Flow
Implementations answer client negotiation requests before normal RPC calls. The default behavior is often delegated to `ProtocolSignature.getProtocolSignature(...)`.

## State And Persistence
The interface defines no state. Implementations may compute signatures from class metadata.

## Dependencies And Integration Points
Integrated with Hadoop RPC protocol negotiation, `RPC.getProtocolVersion`, `ProtocolSignature`, and client-side compatibility checks.

## Risks And Edge Cases
Incorrect versions or method hashes can break rolling upgrades and client/server compatibility. Removing legacy support can affect downstream Hadoop ecosystem projects.

## Test Signals
Protocol compatibility tests should verify version mismatch handling, method support lookup, and rolling-upgrade compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/VersionedProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedRoundRobinMultiplexer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedRoundRobinMultiplexer.java

## Purpose
`WeightedRoundRobinMultiplexer` selects the next FairCallQueue priority queue to poll, giving high-priority queues more turns while still periodically serving lower-priority queues.

## Important APIs, Types, And Functions
- Config key `faircallqueue.multiplexer.weights`, used under the supplied namespace.
- Constructor validates positive queue count, loads configured weights, or builds defaults.
- `getAndAdvanceCurrentIndex()` returns the current queue index then decrements the remaining quota.
- Default weights are powers of two, with the highest-priority index receiving the largest weight and the last queue receiving one.

## Control Flow
The multiplexer starts at queue 0 with its weight as `requestsLeft`. Each call returns `currentQueueIndex`, decrements `requestsLeft`, and when it reaches exactly zero advances to the next queue modulo `numQueues` and resets the quota to that queue's weight. Atomic fields allow concurrent callers without coarse locking; races may produce extra reads from a queue, which the class documents as acceptable.

## State And Persistence
State is in-memory only: `currentQueueIndex`, `requestsLeft`, `queueWeights`, and `numQueues`.

## Dependencies And Integration Points
Implements `RpcMultiplexer` for FairCallQueue-like scheduling. Depends on Hadoop `Configuration` and namespace conventions shared with IPC scheduler configuration.

## Risks And Edge Cases
Configured weights must match the queue count exactly; zero or negative weights are not explicitly rejected and would cause strange advancement behavior. Atomic races can overdraw a queue quota by design. Default weight doubling can overflow for very large queue counts, though practical queue counts are small.

## Test Signals
Tests should verify constructor validation, configured/default weight order, cycle distribution, concurrent access tolerance, and invalid weight-count failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedRoundRobinMultiplexer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedTimeCostProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedTimeCostProvider.java

## Purpose
`WeightedTimeCostProvider` computes an RPC cost as the weighted sum of `ProcessingDetails` timing buckets for use by `DecayRpcScheduler`.

## Important APIs, Types, And Functions
- Config suffix prefix `WEIGHT_CONFIG_PREFIX = ".weighted-cost."`.
- Defaults: lock-free, response, and handler time weight 1; shared lock time weight 10; exclusive lock time weight 100; all other timings weight 0.
- `init(String namespace, Configuration conf)` builds one weight per `ProcessingDetails.Timing`.
- `getCost(ProcessingDetails details)` multiplies each timing value by its configured weight.

## Control Flow
Initialization iterates over all timing enum values, chooses defaults, reads optional integer overrides from `<namespace>.weighted-cost.<timing-lowercase>`, and stores them by ordinal. Cost computation iterates the same enum order and sums `details.get(timing) * weight`.

## State And Persistence
Only the initialized `long[] weights` is stored in memory. There is no persistence.

## Dependencies And Integration Points
Implements `CostProvider` and integrates with `DecayRpcScheduler`, `ProcessingDetails`, and IPC cost-provider configuration.

## Risks And Edge Cases
`getCost` relies on prior `init`; the guard is an `assert`, so production JVMs with assertions disabled could throw a null-pointer instead. Negative or very large weights are not rejected. Enum ordinal coupling is safe only while weights are rebuilt from the same enum order.

## Test Signals
Tests should verify default cost composition, per-timing overrides, ignored queue/wait timings by default, negative/large override behavior if supported, and call-before-init failure mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedTimeCostProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/ShadedProtobufHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/ShadedProtobufHelper.java

## Purpose
`ShadedProtobufHelper` centralizes helper code for Hadoop's shaded protobuf RPC implementation, especially exception conversion, ByteString reuse, token/proto conversion, and concise protobuf IPC calls.

## Important APIs, Types, And Functions
- `getRemoteException(ServiceException se)` returns the wrapped `IOException` cause or a new `IOException` wrapping the service exception.
- `getFixedByteString(Text)` and `getFixedByteString(String)` cache ByteStrings for fixed small string sets.
- `getByteString(byte[])` returns `ByteString.EMPTY` for empty arrays or copies non-empty arrays.
- `tokenFromProto(TokenProto)` builds a Hadoop `Token` from proto identifier/password/kind/service.
- `protoFromToken(Token<?>)` builds a `TokenProto` using cached fixed fields for kind and service.
- `ipc(IpcCall<T>)` executes a lambda and translates shaded protobuf `ServiceException` into `IOException`.
- `IpcCall<T>` is a functional interface for calls throwing `ServiceException`.

## Control Flow
The helper has only static methods. The cache methods look up by the provided key and populate `FIXED_BYTESTRING_CACHE` on miss. Text keys are copied into a new `Text` object so later mutation of the input `Text` cannot corrupt the cache key. `ipc` wraps protobuf stub calls and normalizes exception handling for translators.

## State And Persistence
The only state is a process-wide `ConcurrentHashMap<Object, ByteString>` with no expiration. Token conversions allocate new token/proto objects and do not persist data.

## Dependencies And Integration Points
Used by shaded protobuf client-side translators in Hadoop IPC. Depends on shaded `ByteString`, `ServiceException`, Hadoop `Text`, security `Token`, and `TokenProto`.

## Risks And Edge Cases
The fixed ByteString cache is intentionally unbounded; callers must restrict it to small fixed string domains. Mixed `String` and `Text` keys coexist as different key types. `getRemoteException` preserves only `IOException` causes; non-IO causes become a wrapper `IOException`.

## Test Signals
Tests should verify exception conversion with null, IO, and non-IO causes; Text mutation after caching; empty byte-array singleton behavior; token round-trips; and translator lambdas converting `ServiceException` to `IOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/ShadedProtobufHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/package-info.java

## Purpose
Declares `org.apache.hadoop.ipc.internal` as internal Hadoop IPC implementation space, limited to selected Hadoop modules and unstable.

## Important APIs, Types, And Functions
- Package annotations: `@InterfaceAudience.LimitedPrivate({"HDFS", "MapReduce", "YARN"})` and `@InterfaceStability.Unstable`.

## Control Flow
No executable control flow.

## State And Persistence
No runtime state or persistence.

## Dependencies And Integration Points
Sets API audience expectations for classes such as `ShadedProtobufHelper`.

## Risks And Edge Cases
Downstream users should not rely on stable signatures. Changes can still affect Hadoop submodules listed in the limited-private audience.

## Test Signals
No direct runtime tests; compatibility and compilation of dependent Hadoop modules are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/DecayRpcSchedulerDetailedMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/DecayRpcSchedulerDetailedMetrics.java

## Purpose
Publishes per-priority queue and processing time metrics for `DecayRpcScheduler`/FairCallQueue deployments.

## Important APIs, Types, And Functions
- Metrics source context `decayrpcschedulerdetailed`.
- `create(String ns)` registers the metrics source under `DecayRpcSchedulerDetailedMetrics.<ns>`.
- `init(int numLevels)` creates one queue metric and one processing metric name per priority level.
- `addQueueTime(int priority, long queueTime)` and `addProcessingTime(int priority, long processingTime)` add samples.
- `shutdown()` unregisters the metrics source.

## Control Flow
Creation builds a `MetricsRegistry` tagged by port/namespace and registers with `DefaultMetricsSystem`. `init` precomputes names and initializes `MutableRatesWithAggregation`. Add methods use the supplied priority as an array index into the precomputed names.

## State And Persistence
Holds metrics registry/name and arrays of metric names in memory. Exported metrics are runtime instrumentation only.

## Dependencies And Integration Points
Depends on Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, and `MutableRatesWithAggregation`. Integrated with scheduler code that knows priority level indexes.

## Risks And Edge Cases
`init` must be called before adding samples. The add methods trust `priority` as a zero-based array index, while display names use `priority + 1`; incorrect caller indexing can throw or misattribute metrics. Sources should be unregistered on shutdown to avoid duplicate registrations in tests or restarts.

## Test Signals
Tests should verify source registration/unregistration, name generation, initialized rate names, priority indexing, and sample updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/DecayRpcSchedulerDetailedMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RetryCacheMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RetryCacheMetrics.java

## Purpose
`RetryCacheMetrics` publishes counters for Hadoop IPC retry-cache activity.

## Important APIs, Types, And Functions
- `create(RetryCache cache)` registers a source named `RetryCache.<cacheName>`.
- Counters: `cacheHit`, `cacheCleared`, `cacheUpdated`.
- Incrementers and getters expose current counter values.

## Control Flow
Construction initializes a registry name from the retry cache. The static factory registers the instance. Callers increment counters on retry-cache events.

## State And Persistence
Metrics counters live in memory and are exported through metrics2; no durable persistence.

## Dependencies And Integration Points
Depends on `RetryCache`, metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, and `MutableCounterLong`.

## Risks And Edge Cases
There is no local `shutdown`; lifecycle must be handled elsewhere or source names can collide in repeated tests. Counter fields are injected/initialized by metrics2 registration.

## Test Signals
Retry-cache tests should verify counter increments and registered source naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RetryCacheMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcDetailedMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcDetailedMetrics.java

## Purpose
`RpcDetailedMetrics` publishes per-RPC-method processing, deferred-processing, and overall request-to-response timing metrics.

## Important APIs, Types, And Functions
- Source name `RpcDetailedActivityForPort<port>`, context `rpcdetailed`.
- `create(int port)` registers with `DefaultMetricsSystem`.
- `init(Class<?> protocol)` initializes rate entries from protocol methods, including `Deferred` and `Overall` prefixes.
- `addProcessingTime`, `addDeferredProcessingTime`, and `addOverallProcessingTime` add samples by RPC call name.
- `shutdown()` unregisters the metrics source.

## Control Flow
`Server` creates this source per listener port and adds samples after calls complete. Deferred calls add both deferred and regular processing metrics when their response is completed.

## State And Persistence
Holds metrics registry/source name and mutable rate aggregators in memory only.

## Dependencies And Integration Points
Used directly by `Server.updateMetrics` and `Server.updateDeferredMetrics`. Depends on metrics2 `MutableRatesWithAggregation`.

## Risks And Edge Cases
Protocol initialization must happen before expected method names are reported. Unknown names can still be added dynamically by the metrics object, but method-level observability may drift. Shutdown is needed to avoid duplicate metrics source registration in tests/restarts.

## Test Signals
RPC tests should assert processing/deferred/overall samples are added with correct names and metrics source unregisters cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcDetailedMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcMetrics.java

## Purpose
`RpcMetrics` publishes aggregate server-level IPC metrics: byte counts, queue/processing/response timings, auth outcomes, backoff, slow calls, requeues, successes, connection counts, queue length, and request rate.

## Important APIs, Types, And Functions
- Source name `RpcActivityForPort<port>`, context `rpc`, tagged with port and server name.
- `create(Server, Configuration)` registers the metrics source.
- Time unit defaults to milliseconds and can be configured by `RPC_METRICS_TIME_UNIT`.
- Quantiles are enabled by percentile intervals plus `RPC_METRICS_QUANTILE_ENABLE`.
- Counter incrementers cover authentication, authorization, sent/received bytes, client backoff, disconnected backoff, slow RPCs, requeues, and successful RPC calls.
- Timing adders cover enqueue, queue, lock wait, processing, response, and deferred processing.
- Getter methods expose last-stat processing/deferred sample counts, mean, standard deviation, slow calls, requeues, authorization successes, and tags.

## Control Flow
Construction reads configuration, creates quantile arrays for each configured interval when enabled, and otherwise relies on metrics2-injected mutable counters/rates. `Server` calls byte incrementers from channel IO, timing adders from call completion, and authentication/authorization/backoff counters from handshake and queue paths. Metric methods annotated with `@Metric` pull live values from the associated `Server`.

## State And Persistence
All metrics are in-memory mutable metrics2 objects. No durable state is written. `shutdown()` unregisters the source.

## Dependencies And Integration Points
Tightly integrated with `Server`, `CommonConfigurationKeys`, metrics2 registry/counters/rates/quantiles, and JMX/metrics sinks that consume metrics2 sources.

## Risks And Edge Cases
Invalid time-unit configuration logs and falls back to milliseconds. Quantile arrays are only allocated when enabled; adders guard with `rpcQuantileEnable`. Last-stat mean/stddev depend on metrics snapshot lifecycle and can be zero/empty early. `numOpenConnectionsPerUser()` returns a JSON string from `Server`, so serialization failure appears as null. Duplicate metrics source names can occur if old sources are not unregistered.

## Test Signals
Tests should verify metrics source tags, configured time-unit fallback, quantile creation and updates, counter increments from server events, live server gauge values, slow-RPC/requeue getters, and unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/package-info.java

## Purpose
Declares the IPC metrics package and marks it private, evolving API.

## Important APIs, Types, And Functions
- Package annotations: `@InterfaceAudience.Private` and `@InterfaceStability.Evolving`.

## Control Flow
No executable control flow.

## State And Persistence
No runtime state or persistence.

## Dependencies And Integration Points
Applies to metrics classes used by Hadoop IPC internals and metrics2/JMX publication.

## Risks And Edge Cases
Private/evolving status means downstream direct use should be avoided, but Hadoop internals rely on source compatibility.

## Test Signals
Compilation and metrics integration tests are the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/package-info.java

## Purpose
Documents `org.apache.hadoop.ipc` as the package for network client/server helpers and Hadoop RPC APIs, with limited-private evolving compatibility expectations.

## Important APIs, Types, And Functions
- Package annotations: limited private to HBase, HDFS, MapReduce, YARN, Hive, and Ozone; stability evolving.
- Notes that changes to `RPC` and `RpcEngine` signatures can break external ASF projects, especially with shaded/unshaded protobuf variants.

## Control Flow
No executable control flow.

## State And Persistence
No runtime state or persistence.

## Dependencies And Integration Points
Applies compatibility guidance to the whole IPC package, including server, client, protocol, scheduler, and protobuf integration classes.

## Risks And Edge Cases
The package is not fully public but has broad ecosystem consumers, so apparently internal signature changes can be breaking.

## Test Signals
Cross-project compatibility, Hadoop module compilation, and RPC integration suites provide signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolClientSideTranslatorPB.java

## Purpose
Client-side adapter translating the Java `GenericRefreshProtocol` API to the shaded protobuf `GenericRefreshProtocolPB` blocking stub.

## Important APIs, Types, And Functions
- Implements `ProtocolMetaInterface`, `GenericRefreshProtocol`, and `Closeable`.
- `refresh(String identifier, String[] args)` builds `GenericRefreshRequestProto`, invokes `rpcProxy.refresh`, and unpacks the response collection.
- `close()` stops the RPC proxy.
- `isMethodSupported(String methodName)` delegates to `RpcClientUtil`.

## Control Flow
The translator converts args to a list, builds the request, invokes the PB stub through `ShadedProtobufHelper.ipc` for exception normalization, then maps each `GenericRefreshResponseProto` to `RefreshResponse`, preserving optional user message, exit status, and sender name when present.

## State And Persistence
Holds only the proxied PB stub. No persistent state.

## Dependencies And Integration Points
Used by clients of the generic refresh admin mechanism. Integrates with Hadoop RPC proxy lifecycle, shaded protobuf protos, and method-support metadata.

## Risks And Edge Cases
`Arrays.asList(args)` requires non-null `args`; null arrays fail before RPC. Missing optional response fields map to message/sender null and return code -1. `close()` stops the shared proxy, so ownership must be clear.

## Test Signals
Translator tests should verify request packing, response unpacking with missing fields, exception conversion, method-support lookup, and proxy close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolPB.java

## Purpose
Defines the protobuf RPC wire interface for `GenericRefreshProtocol`.

## Important APIs, Types, And Functions
- Extends generated `GenericRefreshProtocolService.BlockingInterface`.
- Annotated with Kerberos service principal key.
- `@ProtocolInfo` names `org.apache.hadoop.ipc.GenericRefreshProtocol` version 1.
- Audience limited private to HDFS, stability evolving.

## Control Flow
No implementation; generated service methods are implemented by server-side translators and invoked by client-side translators.

## State And Persistence
No state.

## Dependencies And Integration Points
Integrated with Hadoop RPC protocol registration, security principal resolution, and shaded protobuf generated service classes.

## Risks And Edge Cases
Protocol name/version changes are wire-compatibility changes. Kerberos annotation must match service configuration.

## Test Signals
RPC protocol registration and admin refresh integration tests should verify clients can resolve and call this PB protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolServerSideTranslatorPB.java

## Purpose
Server-side adapter translating protobuf `GenericRefreshProtocolPB.refresh` calls to a Java `GenericRefreshProtocol` implementation.

## Important APIs, Types, And Functions
- Holds a `GenericRefreshProtocol impl`.
- `refresh(RpcController, GenericRefreshRequestProto)` validates identifier, converts args list to array, calls `impl.refresh`, and packs `RefreshResponse` results.
- IOExceptions are wrapped in shaded protobuf `ServiceException`.

## Control Flow
On each PB request, the translator extracts args, rejects requests missing `identifier`, delegates to the implementation, then creates a `GenericRefreshResponseCollectionProto` with one response proto per returned `RefreshResponse`, setting exit status, user message, and sender name.

## State And Persistence
Stateless aside from the delegate reference. Any durable effects are performed by the delegate refresh implementation.

## Dependencies And Integration Points
Used when exposing generic refresh services over Hadoop PB RPC. Depends on generated protos, shaded `ServiceException`, and `GenericRefreshProtocol`.

## Risks And Edge Cases
`setUserMessage` and `setSenderName` are called unconditionally; if `RefreshResponse` returns null for either, generated protobuf setters may reject null. Missing identifier is treated as `ServiceException` with a string rather than an `IOException` cause. Delegate exceptions are surfaced as remote IO failures through client helper conversion.

## Test Signals
Tests should cover missing identifier, arg conversion, response packing including null fields if possible, and IOException-to-ServiceException translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolClientSideTranslatorPB.java

## Purpose
Client-side adapter translating `RefreshCallQueueProtocol.refreshCallQueue()` to the shaded protobuf PB protocol.

## Important APIs, Types, And Functions
- Implements `ProtocolMetaInterface`, `RefreshCallQueueProtocol`, and `Closeable`.
- Uses singleton empty `RefreshCallQueueRequestProto`.
- `refreshCallQueue()` invokes the PB proxy through `ShadedProtobufHelper.ipc`.
- `isMethodSupported` delegates to `RpcClientUtil`; `close` stops the proxy.

## Control Flow
The no-argument Java call is converted into an empty protobuf request and sent to `rpcProxy.refreshCallQueue`. The response is ignored; exceptions are converted from `ServiceException` to `IOException`.

## State And Persistence
Holds only the PB proxy and a static immutable request. No local persistence.

## Dependencies And Integration Points
Used by admin clients that trigger live call-queue refresh on RPC servers. Integrates with Hadoop RPC proxy lifecycle and protocol metadata.

## Risks And Edge Cases
Stopping the proxy in `close()` affects shared proxy owners. Because the request is empty, all behavior depends on the server-side delegate and server authorization.

## Test Signals
Tests should verify a PB call is made, exceptions convert to IOExceptions, method support is queried with the correct protocol version, and proxy close stops the proxy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolPB.java

## Purpose
Defines the protobuf RPC wire interface for `RefreshCallQueueProtocol`.

## Important APIs, Types, And Functions
- Extends generated `RefreshCallQueueProtocolService.BlockingInterface`.
- Annotated with Kerberos service principal key.
- `@ProtocolInfo` names `org.apache.hadoop.ipc.RefreshCallQueueProtocol` version 1.
- Audience limited private to HDFS, stability evolving.

## Control Flow
No implementation in this interface; translators provide client/server behavior.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by Hadoop RPC to register and expose the refresh-call-queue admin protocol.

## Risks And Edge Cases
Protocol name/version and Kerberos metadata are compatibility-sensitive.

## Test Signals
Admin protocol tests should verify PB registration, security principal resolution, and successful refresh invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolServerSideTranslatorPB.java

## Purpose
Server-side adapter translating protobuf `refreshCallQueue` requests to a Java `RefreshCallQueueProtocol` implementation.

## Important APIs, Types, And Functions
- Holds a `RefreshCallQueueProtocol impl`.
- Static empty `RefreshCallQueueResponseProto`.
- `refreshCallQueue(RpcController, RefreshCallQueueRequestProto)` delegates to `impl.refreshCallQueue()` and returns the empty response.

## Control Flow
Each protobuf request triggers the delegate refresh method. IOExceptions are wrapped in shaded protobuf `ServiceException`; success returns the prebuilt empty response.

## State And Persistence
Only the delegate reference and static response object are local. Actual server queue state changes happen inside the delegate implementation, commonly `Server.refreshCallQueue`.

## Dependencies And Integration Points
Integrated with Hadoop admin RPC endpoints and call queue refresh plumbing.

## Risks And Edge Cases
The request contents are ignored, so future request fields would need explicit handling. Exceptions rely on client translators to convert `ServiceException` back to `IOException`.

## Test Signals
Tests should cover delegate invocation, IOException wrapping, and empty success response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServlet.java

## Purpose
`JMXJsonServlet` exposes read-only JMX MBean data as JSON under Hadoop HTTP servers, supporting broad bean queries and single-attribute lookup.

## Important APIs, Types, And Functions
- `init()` stores the platform `MBeanServer` and a Jackson `JsonFactory`.
- `isInstrumentationAccessAllowed(...)` delegates access control to `HttpServer2`.
- `doTrace(...)` rejects TRACE requests.
- `doGet(...)` checks instrumentation access, sets JSON/CORS headers, parses `get` and `qry` parameters, and writes JSON.
- `listBeans(...)` queries object names, fetches MBean info/attributes, writes bean objects, and sets 400/404 status on malformed or missing resources.
- `writeAttribute(...)` filters unreadable/unsafe attribute names and serializes values.
- `writeObject(...)` serializes nulls, arrays, numbers, booleans, `CompositeData`, `TabularData`, extra subclass-defined values, and fallback strings.
- `extraCheck`/`extraWrite` are subclass extension hooks.

## Control Flow
For GET requests, access control runs first. A `get` parameter must split into exactly `ObjectName::Attribute`; otherwise the servlet writes an error and returns HTTP 400. Without `get`, `qry` defaults to `*:*`. The servlet starts a JSON object, writes a `beans` array, queries matching MBeans, skips beans that disappear or cannot be introspected, writes `name` and `modelerType`, then either writes a requested attribute or all readable safe attributes. Attribute values recurse through arrays and OpenMBean composite/tabular types.

## State And Persistence
State is servlet-local transient references to the platform MBean server and JSON factory. Responses are generated on demand; no durable persistence.

## Dependencies And Integration Points
Integrated with `HttpServer2` instrumentation authorization, servlet containers, Java ManagementFactory/MBeanServer, Jackson streaming JSON, OpenMBean types, and Hadoop web UIs.

## Risks And Edge Cases
The endpoint exposes operational state and must be protected by instrumentation access checks. Attribute getters can throw runtime exceptions or errors; the servlet logs and skips many failures. Number serialization uses `writeNumber(n.toString())`, which can fail for non-JSON numeric strings such as NaN unless subclasses intercept. Attribute names containing `=`, `:`, or space are skipped to avoid JSON/semantic issues. For single-attribute missing values, the method closes the JSON generator and sets 404 inside `listBeans`, which makes response finalization order sensitive. CORS origin is `*`.

## Test Signals
Tests should cover default and filtered queries, malformed `get`, missing attributes, composite/tabular/array serialization, forbidden instrumentation access, TRACE rejection, disappearing MBeans, unsupported getter exceptions, and subclass `extraCheck` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServletNaNFiltered.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServletNaNFiltered.java

## Purpose
`JMXJsonServletNaNFiltered` customizes `JMXJsonServlet` to serialize values whose string form is `NaN` as numeric `0.0`, avoiding invalid JSON number output.

## Important APIs, Types, And Functions
- Overrides `extraCheck(Object value)` to return true when `Objects.toString(value).trim()` equals `NaN`.
- Overrides `extraWrite(...)` to log and write `0.0`.

## Control Flow
During `JMXJsonServlet.writeObject`, subclass `extraCheck` runs before generic `Number` handling. Matching values are passed to `extraWrite`, which writes a replacement numeric value.

## State And Persistence
Stateless except for logging. No persistence.

## Dependencies And Integration Points
Depends on the base servlet extension hooks, Jackson `JsonGenerator`, and SLF4J. Intended for Hadoop web endpoints whose metrics wrappers may produce NaN-like values without implementing `Number`.

## Risks And Edge Cases
Any object whose trimmed string is exactly `NaN` is coerced to `0.0`, which preserves JSON validity but may hide missing/undefined metric semantics. Case variants such as `nan` are not matched.

## Test Signals
Tests should verify string-like and wrapper NaN values become `0.0`, normal numbers still serialize normally, and recursive array/composite paths apply the filter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServletNaNFiltered.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/package-info.java

## Purpose
Documents `org.apache.hadoop.jmx` as the package exposing JMX access primarily through `JMXJsonServlet`.

## Important APIs, Types, And Functions
- Package annotation: `@InterfaceAudience.Private`.

## Control Flow
No executable control flow.

## State And Persistence
No runtime state or persistence.

## Dependencies And Integration Points
Applies audience metadata to the JMX servlet package used by Hadoop HTTP servers.

## Risks And Edge Cases
Private audience signals no compatibility guarantee for external consumers.

## Test Signals
Compilation and web/JMX servlet integration tests are the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogLevel.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogLevel.java

## Purpose
`LogLevel` provides a runtime log-level inspection and mutation tool for Hadoop daemons, with both a command-line client and an HTTP servlet.

## Important APIs, Types, And Functions
- Constants define usage text and supported protocols `http`/`https`.
- `main` runs `CLI` through `ToolRunner`.
- `isValidProtocol(String)` accepts only exact lowercase `http` or `https`.
- `CLI` parses `-getlevel <host:port> <classname>`, `-setlevel <host:port> <classname> <level>`, and optional `-protocol`.
- `CLI.connect(URL)` uses `AuthenticatedURL` with `KerberosAuthenticator`; HTTPS configures `SSLFactory` and an `SSLSocketFactory`.
- `CLI.process(String)` connects and prints servlet output lines prefixed by `MARKER` after stripping HTML tags.
- `Servlet.doGet` checks administrator access, renders an HTML form, reads `log` and `level` parameters, and delegates log4j logger mutation.
- `Servlet.process(Logger, String, PrintWriter)` validates the requested level via `Level.toLevel`, sets it when valid, and prints the effective level.

## Control Flow
The CLI parses exactly one operation and at most one protocol, defaults protocol to HTTP, constructs the servlet URL, authenticates, reads the HTML response, and prints only marked output lines. The servlet enforces admin access first, initializes an HTML response, resolves the requested SLF4J logger, verifies whether it is backed by log4j via `GenericsUtil.isLog4jLogger`, optionally sets the log4j level, always reports the effective level for log4j loggers, and renders forms.

## State And Persistence
The CLI stores parsed arguments in memory. The servlet changes runtime log4j logger level in the daemon JVM; this is process-local mutable state and is not persisted across restart unless logging configuration is separately changed.

## Dependencies And Integration Points
Integrates with Hadoop `Tool`, `Configuration`, generic options, SPNEGO/Kerberos authentication, optional SSL client configuration, `HttpServer2` administrator authorization, servlet utilities, SLF4J/log4j bridging, and daemon web UIs mounted at `/logLevel`.

## Risks And Edge Cases
CLI query parameters are concatenated without URL encoding, so class names or levels with special characters could produce malformed requests. Protocol validation is case-sensitive. HTTPS `SSLFactory` is initialized but not explicitly destroyed. Servlet output includes submitted logger names in HTML; it relies on servlet utilities and controlled values for safety. Runtime level mutation is restricted to log4j-backed loggers; non-log4j loggers can be inspected only to the extent of the message saying mutation is unsupported. `Level.toLevel` maps unknown strings to DEBUG by default, so the code compares the normalized value to the original to reject invalid levels.

## Test Signals
Tests should cover CLI parsing errors, duplicate operations/protocols, default protocol, HTTP/HTTPS connection setup, marker/tag stripping, servlet admin denial, get-level and set-level flows, invalid levels, non-log4j logger behavior, and persistence expectations across daemon restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogLevel.java -->

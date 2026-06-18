# subset-b-007987 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DecayRpcScheduler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DecayRpcScheduler.java

## Purpose

`DecayRpcScheduler` is the non-default RPC scheduler that assigns calls to priority levels based on decayed per-identity call cost. It tracks caller cost over time, periodically decays historical cost, computes queue priorities, optionally backs off lower-priority callers when recent response time is high, and exports scheduler state through JMX and Metrics2.

## Important APIs, types, and functions

The class implements `RpcScheduler`, `DecayRpcSchedulerMXBean`, and `MetricsSource`. Its constructor reads namespace-scoped configuration for decay period, decay factor, thresholds, identity provider, cost provider, response-time backoff, and top-user metric count. `getPriorityLevel(Schedulable)` returns a queue index, `shouldBackOff(Schedulable)` evaluates response-time backoff, `addResponseTime()` records both call cost and queue/processing latency, and `stop()` unregisters metrics. Package-visible helpers such as `forceDecay()`, `getThresholds()`, and `getCallCostSnapshot()` are test hooks.

`DecayTask` is a weak-reference `TimerTask` that drives periodic decay. `MetricsProxy` is a namespace singleton that keeps a weak delegate and exposes `DecayRpcSchedulerMXBean`/`MetricsSource` without pinning old scheduler instances.

## Control flow

Construction validates `numLevels`, parses config, creates response-time arrays, schedules a daemon `Timer`, installs a metrics proxy, and initializes the scheduling cache. Incoming completed calls enter through `addResponseTime()`: the identity and cost are computed, raw and decayed counters are incremented, then response-time totals for the call's current priority are accumulated. `getPriorityLevel()` normalizes identity, checks the immutable cache, and computes a fallback priority when the cache has no entry.

Each timer tick runs `decayCurrentCosts()`. It multiplies each decayed cost by `decayFactor`, removes identities whose decayed cost reaches zero, recomputes total decayed/raw volumes, atomically swaps a new unmodifiable decision cache, and rolls current-window response-time totals into last-window averages. Priority computation compares the identity's decayed-cost share against thresholds from highest level down.

## State and persistence behavior

All state is in-memory. `callCosts` maps identity to two `AtomicLong`s: decayed cost and raw cost. Totals are held in `AtomicLong`s; response-time metrics are in atomic arrays; `scheduleCacheRef` points at the latest read-only decision map. Static priorities are stored in a plain `HashMap` for special users. No scheduler state is persisted across process restart.

## Dependencies and integration points

The scheduler plugs into `Server` through the `RpcScheduler` interface and into `FairCallQueue` via `Schedulable.getPriorityLevel()`. Identity and cost are supplied by configurable `IdentityProvider` and `CostProvider` implementations, defaulting to `UserIdentityProvider` and `DefaultCostProvider`. Metrics integrate with `DefaultMetricsSystem`, `MBeans`, `RpcMetrics.TIMEUNIT`, and Jackson JSON summaries.

## Risks and test signals

Concurrency risk centers on maintaining consistency between per-identity atomics, totals, and the periodically swapped cache; stale scheduling decisions are expected between decay sweeps. `staticPriorities` is a non-concurrent `HashMap`, so external priority mutation should be limited. `getIdentity()` maps null provider output to `IdentityProvider.Unknown`, but `addResponseTime()` calls `identityProvider.makeIdentity()` directly before `addCost()`, so custom providers returning null can create a null key. Tests should cover config validation, deprecated key fallback, threshold math, decay cleanup, static priority clamping, response-time backoff, metrics/JMX proxy replacement, and local Ozone signals such as `TestDecayRpcSchedulerUtil`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DecayRpcScheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DecayRpcSchedulerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DecayRpcSchedulerMXBean.java

## Purpose

This interface defines the JMX view for `DecayRpcScheduler`. It exposes scheduling decisions, call volume, identity count, response-time averages, and last-window call counts to operators and metrics proxies.

## Important APIs, types, and functions

The API is read-only: `getSchedulingDecisionSummary()`, `getCallVolumeSummary()`, `getUniqueIdentityCount()`, `getTotalCallVolume()`, `getAverageResponseTime()`, and `getResponseTimeCountInLastWindow()`.

## Control flow

There is no local control flow. `DecayRpcScheduler` and its `MetricsProxy` implement this interface, with the proxy delegating to the active scheduler when its weak reference is still live.

## State and persistence behavior

The interface owns no state. Implementations return in-memory scheduler snapshots, usually arrays copied from atomic arrays or JSON derived from current maps.

## Dependencies and integration points

It is registered as an MBean by `DecayRpcScheduler.MetricsProxy` under the scheduler namespace. Consumers are JMX/metrics tooling and tests that inspect scheduler behavior.

## Risks and test signals

Array-returning methods should return snapshots rather than mutable internal arrays. Tests should verify proxy behavior after scheduler replacement or garbage collection and confirm summaries remain valid JSON or clear error strings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DecayRpcSchedulerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DefaultCostProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DefaultCostProvider.java

## Purpose

`DefaultCostProvider` is the baseline `CostProvider` used when no custom provider is configured. It gives every completed RPC the same scheduler cost.

## Important APIs, types, and functions

`init(String, Configuration)` is a no-op. `getCost(ProcessingDetails)` always returns `1`, ignoring the passed timing details.

## Control flow

`DecayRpcScheduler.parseCostProvider()` instantiates this class when configuration provides no `CostProvider`. Every `addResponseTime()` call then increments caller cost by one.

## State and persistence behavior

The class is stateless and persists nothing.

## Dependencies and integration points

It implements `CostProvider` and depends only on Hadoop `Configuration` and `ProcessingDetails`. It is the compatibility path for count-based scheduling rather than time-weighted scheduling.

## Risks and test signals

The main risk is semantic: expensive RPCs and cheap RPCs are treated equally. Tests should assert the no-op initialization contract and constant cost, and scheduler tests should include both default and custom provider paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DefaultCostProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DefaultRpcScheduler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DefaultRpcScheduler.java

## Purpose

`DefaultRpcScheduler` is the no-op scheduler implementation. It keeps all calls at priority `0`, never asks callers to back off, and ignores response-time reporting.

## Important APIs, types, and functions

The constructor accepts the same shape as configurable schedulers but stores nothing. `getPriorityLevel()` returns `0`, `shouldBackOff()` returns `false`, `addResponseTime()` is empty, and `stop()` is empty.

## Control flow

Server setup can instantiate this scheduler as a drop-in when prioritization is disabled. Calls pass through without changing queue placement or backoff behavior.

## State and persistence behavior

There is no mutable or persistent state.

## Dependencies and integration points

It implements `RpcScheduler` and serves as the compatibility baseline for `Server`/`CallQueueManager` integrations.

## Risks and test signals

The risk is configuration drift: deployments expecting fair queuing receive FIFO-equivalent priority hints if this scheduler is selected. Tests should verify zero-priority/no-backoff behavior and that `stop()` is harmless.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DefaultRpcScheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ExternalCall.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ExternalCall.java

## Purpose

`ExternalCall<T>` adapts a `PrivilegedExceptionAction<T>` into a `Server.Call` that can be executed by the IPC handler machinery while an external caller waits for completion. It is used for postponed or externally triggered work that still needs IPC call accounting and response completion semantics.

## Important APIs, types, and functions

The constructor stores the action. `getRemoteUser()` is abstract for subclasses. `get()` blocks until completion and either returns the result or throws `ExecutionException`. `run()` executes the action and sends or aborts the response. `doResponse()` is the completion callback that records the error, marks `done`, and notifies waiters. `getDetailedMetricsName()` returns `(external)`.

## Control flow

The external caller creates a subclass, submits it as a `Server.Call`, and waits in `get()`. The IPC handler invokes `run()`, which calls `action.run()`, then `sendResponse()` on success or `abortResponse()` on failure. Response completion ultimately invokes `doResponse()`, which releases the waiter.

## State and persistence behavior

State is per-call and in-memory: action, atomic completion flag, result, and error. There is no durable state.

## Dependencies and integration points

It extends `Server.Call`, uses `RpcStatusProto`, and depends on `UserGroupInformation` for remote user attribution. Ozone tests such as `TestS3SecretRequestHelper` use stub subclasses.

## Risks and test signals

Wait/notify correctness is critical. `waitForCompletion()` loops on an `AtomicBoolean` while synchronizing on the same object; tests should cover normal completion, exception completion, interrupted waits, double response attempts, and postponed-call behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ExternalCall.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/FairCallQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/FairCallQueue.java

## Purpose

`FairCallQueue` is a multi-level `BlockingQueue` for RPC calls. It stores calls in priority-specific subqueues, uses a pluggable multiplexer to choose dequeue order, tracks overflow counts, and exports queue metrics.

## Important APIs, types, and functions

The constructor creates `priorityLevels` `LinkedBlockingQueue`s, distributing total capacity with remainder assigned to priority `0`, creates overflow counters, installs a `WeightedRoundRobinMultiplexer`, and registers a metrics proxy. Queue operations include `add()`, `put()`, `offer()`, timed `offer()`, `take()`, `poll()`, `peek()`, `drainTo()`, `remainingCapacity()`, `getQueueSizes()`, `getOverflowedCalls()`, and `setMultiplexer()`.

`MetricsProxy` is a namespace singleton implementing `FairCallQueueMXBean` and `MetricsSource`, delegating through a weak reference and incrementing `revisionNumber` each time the active queue changes.

## Control flow

Producers use the `Schedulable` priority level. `add()` tries the requested queue and lower-priority queues, throwing `CallQueueOverflowException.DISCONNECT` only when the lowest-priority queue overflows and `KEEPALIVE` otherwise. `put()` tries all but the last queue and blocks on the last when necessary. `offer()` targets only the requested queue. Successful inserts release one semaphore permit.

Consumers acquire a semaphore permit before removing. `removeNextElement()` asks the multiplexer for a starting queue, polls it, and if empty scans all queues until it removes an element. This preserves the invariant that each acquired permit corresponds to one removed item despite races among consumers.

## State and persistence behavior

State is runtime-only: subqueue objects, semaphore permits, multiplexer, overflow counters, and metrics proxy delegate. `size()` reports semaphore permits, not a locked sum of subqueue sizes. No queue contents are persisted.

## Dependencies and integration points

The queue integrates with `CallQueueManager`, `Schedulable`, `RpcMultiplexer`, `WeightedRoundRobinMultiplexer`, JMX via `MBeans`, and Metrics2 via `DefaultMetricsSystem`. Overflow exceptions inform RPC connection behavior.

## Risks and test signals

Consistency is deliberately weak for `poll()`, `peek()`, and metrics snapshots. `drainTo()` drains permits first and restores unused permits; tests should verify no permit leaks under partial drains. `iterator()` is intentionally unimplemented. Useful tests cover capacity distribution, overflow behavior by priority, semaphore/subqueue synchronization under concurrency, multiplexer fairness, metrics revision changes, and weak-reference proxy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/FairCallQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/FairCallQueueMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/FairCallQueueMXBean.java

## Purpose

This interface defines the JMX contract for `FairCallQueue` queue sizes, overflow counts, and delegate revision.

## Important APIs, types, and functions

`getQueueSizes()` returns per-priority subqueue sizes, `getOverflowedCalls()` returns per-priority overflow counters, and `getRevision()` reports how many times the metrics proxy has been pointed at a queue.

## Control flow

There is no local control flow. `FairCallQueue.MetricsProxy` implements the interface and delegates to the current queue if available.

## State and persistence behavior

The interface owns no state. Implementations expose in-memory snapshots only.

## Dependencies and integration points

It is registered by `FairCallQueue` through Hadoop `MBeans` and consumed by operators, metrics tooling, and tests.

## Risks and test signals

Tests should confirm empty arrays when no delegate exists, stable array lengths matching priority levels, and revision increments after delegate replacement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/FairCallQueueMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/IdentityProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/IdentityProvider.java

## Purpose

`IdentityProvider` abstracts how a scheduler derives a caller identity from a `Schedulable`. This lets deployments choose whether scheduling groups by user, caller context, or another request attribute.

## Important APIs, types, and functions

The single method `makeIdentity(Schedulable obj)` returns a scheduling identity string or `null` if the provider cannot derive one.

## Control flow

`DecayRpcScheduler` calls providers when computing priority and recording cost. Its `getIdentity()` wrapper maps null to a fixed unknown identity for priority lookup.

## State and persistence behavior

The interface has no state. Implementations may be stateless or configuration-backed, but this file does not prescribe persistence.

## Dependencies and integration points

It depends on `Schedulable` and is configured through `CommonConfigurationKeys.IPC_IDENTITY_PROVIDER_KEY`. The default implementation in this package is `UserIdentityProvider`.

## Risks and test signals

Provider null handling must be consistent across all scheduler entry points. Tests should cover null identities, missing UGI, caller-context identities if implemented, and custom provider loading.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/IdentityProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/IpcException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/IpcException.java

## Purpose

`IpcException` is a simple `IOException` subtype for IPC-layer connection establishment failures.

## Important APIs, types, and functions

It provides a single public constructor accepting an error string and inherits `IOException` behavior.

## Control flow

Callers throw this exception when IPC setup cannot proceed. There is no additional local flow.

## State and persistence behavior

The only state is the inherited exception message and stack trace. Nothing is persisted.

## Dependencies and integration points

It integrates with client/server connection code through Java checked exception handling.

## Risks and test signals

Tests should only need to verify message propagation and catchability as `IOException`. The class does not carry RPC status codes, so wire-level mappings must happen elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/IpcException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProcessingDetails.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProcessingDetails.java

## Purpose

`ProcessingDetails` records per-call timing for each IPC processing phase. It feeds scheduler cost/backoff logic, detailed metrics, and diagnostic logging.

## Important APIs, types, and functions

The `Timing` enum covers `ENQUEUE`, `QUEUE`, `HANDLER`, `PROCESSING`, lock-free/wait/shared/exclusive subphases, and `RESPONSE`. The package-private constructor fixes the internal `TimeUnit`. `get()`, `get(..., TimeUnit)`, `set()`, `set(..., TimeUnit)`, and `add()` manipulate timing values. `toString()` emits all timings as lower-case `*Time=` fields.

## Control flow

IPC code creates a details object for a call, records durations as the call moves through reader, queue, handler, processing, lock, and response stages, then passes the object to scheduler and metrics paths. `get()` clamps negative values to zero to handle rare `nanoTime` anomalies.

## State and persistence behavior

State is a per-call `long[]` indexed by enum ordinal plus the internal value time unit. Nothing is persisted.

## Dependencies and integration points

`DecayRpcScheduler` reads `QUEUE` and `PROCESSING` in `RpcMetrics.TIMEUNIT`; cost providers can read any timing. Ozone integration tests include `testProcessingDetails()` in filesystem test coverage.

## Risks and test signals

Enum ordinal indexing means reordering `Timing` values changes serialized/logical interpretation inside the object. Tests should cover unit conversion, additive updates, negative-value clamping, `toString()` field order, and the invariant that `PROCESSING` equals lock subphase totals when maintained by callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProcessingDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtoUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtoUtil.java

## Purpose

`ProtoUtil` centralizes protobuf conversions for IPC connection context and request headers. It bridges Java RPC/security state into generated protobuf messages.

## Important APIs, types, and functions

`makeIpcConnectionContext()` builds `IpcConnectionContextProto` with protocol and user information based on `AuthMethod`. `getUgi()` reconstructs `UserGroupInformation` from connection context or user info. `convert()` maps between `RPC.RpcKind` and `RpcKindProto`. `makeRpcRequestHeader()` builds `RpcRequestHeaderProto` with kind, operation, call ID, retry count, client ID, optional `CallerContext`, and optional `AlignmentContext` state.

## Control flow

For Kerberos, the connection context sends only effective user because real user comes from authentication. For token auth, no user fields are sent. For simple auth, effective and optional real users are included. Request header creation always sets core fields, then conditionally attaches caller context and alignment information.

## State and persistence behavior

The class is static and stateless. It creates protobuf messages for network transmission but stores nothing locally.

## Dependencies and integration points

It depends on generated IPC protobuf classes, `SaslRpcServer.AuthMethod`, `UserGroupInformation`, `CallerContext`, `AlignmentContext`, and `RPC.RpcKind`. It is used by client connection setup and per-call request framing.

## Risks and test signals

Security semantics are sensitive to auth method: leaking real users for token/Kerberos or omitting users for simple auth would break impersonation. Tests should cover each auth method, proxy-user reconstruction, unknown enum conversions returning null, caller-context signatures, alignment context mutation, and UUID/client ID byte preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtoUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufHelper.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufHelper.java

## Purpose

`ProtobufHelper` provides a small helper for converting protobuf `ServiceException` failures back into Java `IOException`s expected by Hadoop RPC callers.

## Important APIs, types, and functions

`getRemoteException(ServiceException se)` returns the cause if it is an `IOException`; otherwise it wraps the `ServiceException` in a new `IOException`. The constructor is private because the class is static-only.

## Control flow

Client code catches `ServiceException` from protobuf stubs and calls this helper. A null cause or non-IO cause is treated as unexpected and wrapped.

## State and persistence behavior

The helper is stateless and persists nothing.

## Dependencies and integration points

It depends on protobuf `ServiceException` and Java `IOException`. It integrates with client-side translator layers that expose checked IO exceptions instead of protobuf exceptions.

## Risks and test signals

Tests should cover `RemoteException` causes, other `IOException` causes, null causes, and non-IO causes. Preserving the original cause chain is important for retry and failover logic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufRpcEngine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufRpcEngine.java

## Purpose

`ProtobufRpcEngine` is the RPC engine for protobuf-based Hadoop protocols. It builds client-side dynamic proxies, serializes protobuf request headers and payloads, creates protobuf RPC servers, and dispatches server-side calls through generated `BlockingService` descriptors.

## Important APIs, types, and functions

The static initializer registers `RPC_PROTOCOL_BUFFER` with `Server.registerProtocolEngine()` and the `RpcProtobufRequest` deserializer. `getProxy()` returns a `ProtocolProxy` backed by an `Invoker`. `getServer()` returns a protobuf-aware `Server`.

`Invoker` implements `RpcInvocationHandler`: it builds request headers, validates protobuf method arguments, calls `Client.call()`, caches return prototypes by method name, deserializes response buffers, exposes `getConnectionId()`, and closes cached clients. `Server` extends `RPC.Server`, registers the protocol implementation, and owns `ProtoBufRpcInvoker`. `RpcProtobufRequest` stores a lazily decoded request header and optional protobuf payload.

## Control flow

Client calls hit the dynamic proxy. The `Invoker` expects exactly two arguments, an RPC controller and protobuf `Message`; it creates `RequestHeaderProto`, wraps header/payload in `RpcProtobufRequest`, sends it through the shared `ClientCache`, and decodes the returned `RpcWritable.Buffer` using the method return type's `getDefaultInstance()`.

On the server, `ProtoBufRpcInvoker.call()` reads the protobuf request header, resolves protocol name and client version against `RPC.Server`'s protocol map, looks up the generated method descriptor, decodes the payload using the service request prototype, initializes detailed metrics, sets thread-local call info, invokes `callBlockingMethod()`, and wraps the result as `RpcWritable`. `ServiceException` causes and other exceptions update detailed metrics before propagating.

## State and persistence behavior

Client state includes a static `ClientCache`, per-proxy `ConnectionId`, cached return protobuf prototypes, fallback auth flag, and optional alignment context. Server state is inherited from `RPC.Server` protocol maps plus a thread-local current call info. No durable state is stored.

## Dependencies and integration points

This file integrates protobuf `Message`, `BlockingService`, and descriptors with Hadoop `Client`, `Server`, `RPC`, `RpcWritable`, `RequestHeaderProto`, `AlignmentContext`, `UserGroupInformation`, `RetryPolicy`, and token secret managers. Many Ozone server/client utilities set protocol engines to `ProtobufRpcEngine`.

## Risks and test signals

Method argument shape, return type reflection, and descriptor lookup are brittle compatibility points for generated protobuf stubs. Static `ClientCache` sharing requires correct `close()`/`stopProxy()` behavior. Tests should cover unknown protocol, version mismatch, unknown method, null parameters, remote `ServiceException` propagation, fallback-to-simple-auth mutation, alignment context propagation, client cache shutdown, and protocol registration through `RPC.Builder`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufRpcEngine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufRpcEngineCallback.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufRpcEngineCallback.java

## Purpose

`ProtobufRpcEngineCallback` is a callback contract for asynchronous protobuf RPC paths. It receives either a protobuf response message or an error.

## Important APIs, types, and functions

`setResponse(Message message)` supplies the successful response. `error(Throwable t)` reports failure.

## Control flow

The interface itself has no flow. Implementations are expected to be called by asynchronous RPC machinery once a server method completes or fails.

## State and persistence behavior

The interface owns no state. Implementations decide how to store or signal completion.

## Dependencies and integration points

It depends on protobuf `Message` and is part of the protobuf RPC engine surface.

## Risks and test signals

Implementations must define single-completion behavior and thread-safety. Tests should verify success/error exclusivity, null handling expectations, and callback invocation on exceptional server paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtobufRpcEngineCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolInfo.java

## Purpose

`ProtocolInfo` is a runtime annotation for overriding the default RPC protocol name and optionally declaring protocol version.

## Important APIs, types, and functions

The annotation has `protocolName()` and `protocolVersion()` elements. `protocolVersion()` defaults to `-1`, which tells `RPC.getProtocolVersion()` to fall back to the legacy `versionID` field.

## Control flow

`RPC.getProtocolName()` and `RPC.getProtocolVersion()` inspect this annotation when registering protocols and constructing client request headers.

## State and persistence behavior

Annotation values are class metadata retained at runtime. There is no mutable state or persistence.

## Dependencies and integration points

It integrates protocol interfaces, generated protobuf translators, and `RPC.Server` protocol maps.

## Risks and test signals

Mismatched names or versions break client/server lookup. Tests should cover annotated name override, annotated version override, fallback to `versionID`, and failure when neither annotation version nor `versionID` is available.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolProxy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolProxy.java

## Purpose

`ProtocolProxy<T>` is a lightweight holder for a client-side proxy object associated with a protocol interface.

## Important APIs, types, and functions

The constructor stores `protocol` and `proxy`; `getProxy()` returns the proxy. The stored protocol field is not otherwise used in this class.

## Control flow

RPC engines return `ProtocolProxy` from `getProxy()`. Callers unwrap it to obtain the dynamic proxy or translator.

## State and persistence behavior

State is just the protocol class reference and proxy instance. Nothing is persisted.

## Dependencies and integration points

It is returned by `RpcEngine.getProxy()` and `RPC.getProtocolProxy()`, and consumed by client setup code.

## Risks and test signals

The class does not validate that the proxy implements the protocol. Tests should cover generic typing, null handling expectations, and downstream `RPC.stopProxy()` behavior on the contained proxy.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolTranslator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolTranslator.java

## Purpose

`ProtocolTranslator` marks client-side translator classes that wrap an underlying RPC proxy. It lets common RPC utilities reach the real proxy when the public client object is an adapter.

## Important APIs, types, and functions

`getUnderlyingProxyObject()` returns the wrapped proxy object.

## Control flow

`RPC.getConnectionIdForProxy()` checks this interface and unwraps before reading the proxy's invocation handler.

## State and persistence behavior

The interface owns no state. Implementations hold the underlying proxy.

## Dependencies and integration points

It integrates translator/adaptor layers with generic RPC utilities such as connection ID lookup and proxy shutdown.

## Risks and test signals

Returning the wrong object breaks diagnostics and connection handling. Tests should cover translated and non-translated proxies, nested translators if used, and behavior when the underlying proxy is already closed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolTranslator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RPC.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RPC.java

## Purpose

`RPC` is the central utility and abstraction layer for Hadoop IPC protocols. It resolves protocol names and versions, manages protocol-to-engine mapping, creates client proxies, closes proxies, builds servers, and maintains server-side protocol implementation maps.

## Important APIs, types, and functions

`RpcKind` identifies built-in, writable, and protobuf RPC kinds. `RpcInvoker` is the server-side dispatch contract. Static helpers include `getProtocolName()`, `getProtocolVersion()`, `setProtocolEngine()`, `getProtocolProxy()`, `getServerAddress()`, `getConnectionIdForProxy()`, `stopProxy()`, and `getRpcTimeout()`. `VersionMismatch` maps version errors to `ERROR_RPC_VERSION_MISMATCH`.

`Builder` captures server settings and constructs an engine-specific server. `RPC.Server` extends the lower-level IPC `Server`, names servers from implementation classes, stores per-kind protocol maps keyed by protocol name/version, registers implementations, exposes supported versions, sets scheduler priority for configured client principals, and dispatches calls through registered invokers.

## Control flow

Client setup calls `getProtocolProxy()`, initializes SASL if security is enabled, resolves the protocol engine from configuration or the default `ProtobufRpcEngine`, and delegates proxy construction. `stopProxy()` closes either a `Closeable` proxy or a closeable invocation handler.

Server setup uses `Builder.build()` to validate mandatory protocol, instance, and configuration, then asks the configured engine to create a server. During registration, `RPC.Server` resolves protocol name/version, stores implementation metadata in the per-kind map, and optionally marks the configured client principal as highest scheduler priority. Incoming calls route through `call()`, which selects the `RpcInvoker` for the request kind.

## State and persistence behavior

Static state includes the process-wide `PROTOCOL_ENGINES` cache. Each server stores protocol implementation maps in memory. No state is persisted; protocol registration must happen at process startup or server construction.

## Dependencies and integration points

`RPC` ties together `Configuration`, `CommonConfigurationKeys`, `Client.ConnectionId`, retry policies, SASL/security utilities, token secret managers, `ReflectionUtils`, lower-level `Server`, and protobuf error codes. It is the primary API used by Ozone code to configure `ProtobufRpcEngine` and create service endpoints.

## Risks and test signals

Protocol version discovery fails at runtime if neither `ProtocolInfo` version nor `versionID` exists. The engine cache is keyed only by protocol class, so configuration changes after first lookup may not take effect. `stopProxy()` throws for mocks or adapters that do not expose closeable handlers. Tests should cover annotation and `versionID` paths, engine cache behavior, secure-client SASL initialization, builder mandatory fields, server name extraction for generated/anonymous classes, unknown protocol/version dispatch, and translated proxy connection lookup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RPC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RemoteException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RemoteException.java

## Purpose

`RemoteException` represents an exception thrown by a remote RPC server. It preserves the remote exception class name, message, and optional protobuf RPC error code, and can attempt to unwrap the remote type locally.

## Important APIs, types, and functions

Constructors accept class name, message, and optional `RpcErrorCodeProto`. `getClassName()` and `getErrorCode()` expose metadata. `unwrapRemoteException(Class<?>...)` unwraps only matching lookup types. `unwrapRemoteException()` tries to load the remote class as an `IOException` subclass. `instantiateException()` requires a public/string constructor, sets the `RemoteException` as cause, and returns the new exception. `valueOf(Attributes)` builds from XML attributes.

## Control flow

Client-side code receives `RemoteException`, optionally calls unwrap, and either gets a more specific local `IOException` or the original `RemoteException`. Unknown class names, non-IO classes, missing constructors, or unmatched lookup classes all fall back to `this`.

## State and persistence behavior

State is immutable exception metadata plus inherited stack trace. It is not persisted except when serialized/logged by callers.

## Dependencies and integration points

It integrates with protobuf RPC response error codes, XML/SAX conversion, failover code, and Ozone tests such as `TestRemoteEx`, `TestSecretKeysApi`, and HA follower-read tests.

## Risks and test signals

Reflection-based unwrapping is sensitive to class availability and constructors. `getErrorCode()` may return null for unspecified or unknown numeric codes. Tests should cover exact lookup unwrapping, generic unwrapping, missing class, class not extending `IOException`, no string constructor, error-code preservation, and `toString()` formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RemoteException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ResponseBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ResponseBuffer.java

## Purpose

`ResponseBuffer` is a reusable byte buffer for length-framed RPC responses. It reserves four leading bytes for payload length and writes response data after that frame header.

## Important APIs, types, and functions

Constructors create a `FramedBuffer` with default or explicit capacity. `writeTo(OutputStream)` updates the frame length and writes the whole framed buffer. Package-visible helpers include `toByteArray()`, `capacity()`, `setCapacity()`, `ensureCapacity()`, and `reset()`. `FramedBuffer` overrides `size()` and `reset()` and writes the big-endian frame length in `setSize()`.

## Control flow

RPC writable wrappers write payload bytes to the `DataOutputStream`. Before output, `getFramedBuffer()` sets the first four bytes to `written`, then the buffer is emitted. `reset()` clears the logical payload and returns the write pointer to just after the framing bytes.

## State and persistence behavior

State is in-memory byte array capacity, byte count, and `DataOutputStream.written`. No data is persisted.

## Dependencies and integration points

It is used by `RpcWritable` and server response encoding paths to avoid extra intermediate arrays and to preserve Hadoop RPC length framing.

## Risks and test signals

Capacity changes must preserve the four framing bytes and existing payload when appropriate. Tests should cover empty response framing, big-endian length bytes, `ensureCapacity()` growth, `reset()` reuse, `writeTo()` length correctness, and large protobuf/writable payloads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ResponseBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RetriableException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RetriableException.java

## Purpose

`RetriableException` signals that a server could not process a request temporarily and the client may retry.

## Important APIs, types, and functions

It extends `IOException` and provides constructors for wrapping an `Exception` or carrying a message string.

## Control flow

Server code throws this when startup, leadership, or another transient condition prevents processing. Client retry/failover layers inspect the exception type or remote wrapping.

## State and persistence behavior

State is inherited exception message/cause/stack trace only.

## Dependencies and integration points

It integrates with Hadoop/Ozone retry policies and remote exception propagation.

## Risks and test signals

Tests should verify retry classification through direct and `RemoteException`-wrapped paths. Overuse can mask permanent failures, so callers should only throw it for genuinely transient states.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RetriableException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcClientException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcClientException.java

## Purpose

`RpcClientException` represents RPC client-side failures within the IPC exception hierarchy.

## Important APIs, types, and functions

It extends `RpcException` and has package-private constructors for message-only and message-with-cause forms.

## Control flow

IPC client internals can throw this subtype when failures are attributable to the client side rather than server response status.

## State and persistence behavior

Only inherited exception state is stored.

## Dependencies and integration points

It integrates with `RpcException` and checked `IOException` handling inside the IPC client package.

## Risks and test signals

Because constructors are package-private, external code cannot create it directly. Tests in the package should cover message/cause propagation and classification distinct from `RpcServerException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcClientException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcConstants.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcConstants.java

## Purpose

`RpcConstants` centralizes wire-level constants for Hadoop IPC connections and special call IDs.

## Important APIs, types, and functions

Constants include special call IDs for authorization failure, invalid calls, connection context, and ping; empty dummy client ID; invalid retry count; the `"hrpc"` connection header as a `ByteBuffer`; post-header byte count; and current wire protocol version `9`.

## Control flow

Connection setup and request framing code read these constants while parsing or emitting headers. There is no executable flow in the class.

## State and persistence behavior

All state is static constants. The public `HEADER` buffer is mutable as a `ByteBuffer` object, so consumers should avoid changing its position or contents.

## Dependencies and integration points

It integrates with low-level `Client` and `Server` connection handshakes and protocol compatibility checks.

## Risks and test signals

Wire compatibility depends on these values. Tests should verify header bytes, version negotiation, special call ID handling, retry-count defaults, and that callers duplicate/read-only-wrap `HEADER` before mutating buffer position.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcEngine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcEngine.java

## Purpose

`RpcEngine` defines the pluggable transport/serialization engine contract used by `RPC`.

## Important APIs, types, and functions

`getProxy()` constructs a client-side protocol proxy for a remote address with security, retry, timeout, fallback-auth, and alignment context inputs. `getServer()` constructs an `RPC.Server` for a protocol implementation with bind, handler, reader, queue, secret manager, port-range, and alignment settings.

## Control flow

`RPC.getProtocolProxy()` resolves an engine and delegates client proxy construction. `RPC.Builder.build()` delegates server construction. Implementations such as `ProtobufRpcEngine` supply the concrete serialization and dispatch behavior.

## State and persistence behavior

The interface owns no state. Engine implementations may cache clients or reflection metadata, but this file does not prescribe persistence.

## Dependencies and integration points

It connects `Configuration`, socket factories, retry policies, UGI, token secret managers, `AlignmentContext`, and `RPC.Server`.

## Risks and test signals

Engine implementations must honor the full parameter surface, especially security and alignment context. Tests should use a fake or protobuf engine to verify `RPC` passes all builder/proxy parameters correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcEngine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcException.java

## Purpose

`RpcException` is the base checked exception for RPC-layer failures that are more specific than plain `IOException`.

## Important APIs, types, and functions

It extends `IOException` and provides package-private constructors for message and message-with-cause.

## Control flow

Subclasses such as `RpcServerException`, `RpcClientException`, `RpcNoSuchMethodException`, and `RpcNoSuchProtocolException` use it to participate in checked exception handling.

## State and persistence behavior

Only inherited exception state is stored.

## Dependencies and integration points

It is the root of the package's typed RPC exception hierarchy and integrates with protobuf response status mapping through subclasses.

## Risks and test signals

The constructors are not public, which keeps external code on defined subclasses. Tests should verify subclass message/cause preservation and serialization compatibility through `serialVersionUID`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcInvocationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcInvocationHandler.java

## Purpose

`RpcInvocationHandler` is the common interface for dynamic proxy handlers used by RPC clients.

## Important APIs, types, and functions

It extends `InvocationHandler` and `Closeable`, and adds `getConnectionId()` to expose the associated `Client.ConnectionId`.

## Control flow

`ProtobufRpcEngine.Invoker` implements this interface. `RPC.getConnectionIdForProxy()` and `RPC.stopProxy()` use it to inspect and close proxies.

## State and persistence behavior

The interface has no state; implementations hold connection/client state.

## Dependencies and integration points

It integrates Java dynamic proxies with Hadoop `Client.ConnectionId` and lifecycle management.

## Risks and test signals

Handlers must be closeable and idempotent enough for `stopProxy()`. Tests should cover connection ID access, close propagation, and translated proxies that unwrap to a handler-backed object.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcInvocationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcMultiplexer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcMultiplexer.java

## Purpose

`RpcMultiplexer` is the strategy interface that chooses which `FairCallQueue` subqueue should be polled next.

## Important APIs, types, and functions

The single method `getAndAdvanceCurrentIndex()` returns the current queue index and may update internal state for the next call.

## Control flow

`FairCallQueue.removeNextElement()` calls the multiplexer after acquiring a semaphore permit. If the chosen queue is empty, `FairCallQueue` scans all queues to satisfy the permit.

## State and persistence behavior

The interface has no state. Implementations such as `WeightedRoundRobinMultiplexer` maintain runtime scheduling cursors.

## Dependencies and integration points

It integrates with `FairCallQueue` and configurable queue fairness policies.

## Risks and test signals

Implementations must return indexes within the configured queue range and be thread-safe enough for concurrent consumers. Tests should cover index bounds, fairness/weight behavior, and behavior when selected queues are empty.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcMultiplexer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcNoSuchMethodException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcNoSuchMethodException.java

## Purpose

`RpcNoSuchMethodException` reports that a requested RPC method is not available on the resolved protocol.

## Important APIs, types, and functions

It extends `RpcServerException`, has a public message constructor, returns `RpcStatusProto.ERROR`, and maps to `RpcErrorCodeProto.ERROR_NO_SUCH_METHOD`.

## Control flow

`ProtobufRpcEngine.ProtoBufRpcInvoker` throws this when the generated `BlockingService` descriptor has no method matching the request header.

## State and persistence behavior

Only exception message and inherited stack/cause state are stored.

## Dependencies and integration points

It integrates server dispatch with protobuf RPC response headers and client-side remote exception handling.

## Risks and test signals

Tests should cover unknown method requests, error-code propagation to clients, and distinction from unknown protocol/version errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcNoSuchMethodException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcNoSuchProtocolException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcNoSuchProtocolException.java

## Purpose

`RpcNoSuchProtocolException` reports that a server does not know the requested RPC protocol.

## Important APIs, types, and functions

It extends `RpcServerException`, has a public message constructor, returns `RpcStatusProto.ERROR`, and maps to `RpcErrorCodeProto.ERROR_NO_SUCH_PROTOCOL`.

## Control flow

Server dispatch throws this when no registered protocol matches the requested protocol name. Ozone HA/failover tests assert this error appears in follower-read failure paths.

## State and persistence behavior

Only inherited exception state is stored.

## Dependencies and integration points

It integrates `RPC.Server`/`ProtobufRpcEngine` protocol lookup with protobuf error codes and remote exception unwrapping.

## Risks and test signals

Tests should cover unknown protocol lookup, error-code propagation, failover handling, and distinction from version mismatch where the protocol exists but the requested version does not.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcNoSuchProtocolException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcScheduler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcScheduler.java

## Purpose

`RpcScheduler` defines the scheduling and backoff contract used by Hadoop IPC servers.

## Important APIs, types, and functions

`getPriorityLevel(Schedulable)` returns a priority hint. `shouldBackOff(Schedulable)` decides whether a caller should be throttled. The deprecated `addResponseTime(String, int, int, int)` exists for old implementations and throws by default. The modern default `addResponseTime(String, Schedulable, ProcessingDetails)` converts queue and processing timings to `RpcMetrics.TIMEUNIT` and delegates to the deprecated method. `stop()` releases scheduler resources.

## Control flow

Server call completion reports processing details to the scheduler. New implementations should override the modern method; old implementations can still receive queue/processing integers through the default bridge.

## State and persistence behavior

The interface has no state. Implementations such as `DecayRpcScheduler` maintain runtime metrics and timers.

## Dependencies and integration points

It integrates `Server.Call`, `Schedulable`, `ProcessingDetails`, `FairCallQueue`, and `RpcMetrics`.

## Risks and test signals

New schedulers that do not override the modern method will hit the deprecated default and likely throw. Tests should verify default bridge behavior, stop lifecycle, priority bounds, and backoff semantics for each scheduler implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcScheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcServerException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcServerException.java

## Purpose

`RpcServerException` is the base class for server-side RPC errors that can be mapped into protobuf response status and error codes.

## Important APIs, types, and functions

It extends `RpcException`, provides public message and message-with-cause constructors, returns `RpcStatusProto.ERROR`, and defaults to `RpcErrorCodeProto.ERROR_RPC_SERVER`.

## Control flow

Server dispatch and validation paths throw this class or subclasses. Response encoding reads `getRpcStatusProto()` and `getRpcErrorCodeProto()` to populate headers.

## State and persistence behavior

Only inherited exception state is stored.

## Dependencies and integration points

It integrates with protobuf `RpcResponseHeaderProto` status/error code fields and the server exception hierarchy.

## Risks and test signals

Subclasses must override error codes when clients need specific retry/failover behavior. Tests should cover default status/code and subclass overrides for no-such-method, no-such-protocol, and version mismatch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcServerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcWritable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcWritable.java

## Purpose

`RpcWritable` is the optimized serialization adapter used by Hadoop IPC for `Writable`, protobuf `Message`, and raw byte-buffer RPC payloads.

## Important APIs, types, and functions

`wrap(Object)` returns an existing `RpcWritable`, a `ProtobufWrapper`, or a `WritableWrapper`. Standard `Writable.readFields()` and `write()` are final and unsupported to force optimized paths. `writeTo(ResponseBuffer)` and `readFrom(ByteBuffer)` are the core internal methods.

`WritableWrapper` delegates serialization to a `Writable` and reads through a `DataInputStream` over a byte-array-backed buffer. `ProtobufWrapper` writes/reads delimited protobuf messages using `CodedOutputStream`/`CodedInputStream`. `Buffer` wraps raw bytes, can instantiate configured value classes, decodes values with `getValue()`, and exposes remaining bytes.

## Control flow

Client and server code wrap response/request objects, write them to `ResponseBuffer`, or receive a `Buffer` and lazily decode it into the expected type. Protobuf decoding consumes only the delimited message and advances the `ByteBuffer` by bytes read. Writable decoding advances the buffer based on consumed bytes.

## State and persistence behavior

Wrappers hold either a mutable protobuf message reference, a writable instance, or a `ByteBuffer` slice. State is per-call and in-memory.

## Dependencies and integration points

It integrates `ResponseBuffer`, Hadoop `Writable`, `Configurable`, `Configuration`, protobuf `Message`, and IPC client/server request decoding. `ProtobufRpcEngine.RpcProtobufRequest` extends `RpcWritable.Buffer`.

## Risks and test signals

The implementation assumes byte-array-backed `ByteBuffer`s. Position/limit advancement is subtle and affects multi-message protobuf request decoding. `valueClass.newInstance()` requires a no-arg constructor. Tests should cover writable round trips, protobuf delimited round trips, buffer slicing, multiple values in one buffer, configurable instantiation, unsupported legacy methods, and direct-buffer rejection or avoidance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Schedulable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Schedulable.java

## Purpose

`Schedulable` is the minimal call metadata contract consumed by RPC schedulers and fair queues.

## Important APIs, types, and functions

`getUserGroupInformation()` returns the remote user. `getCallerContext()` defaults to throwing `UnsupportedOperationException` and is intended to be overridden by `Server.Call`. `getPriorityLevel()` returns the call's assigned priority.

## Control flow

Schedulers inspect a `Schedulable` to derive identities and priority decisions. `FairCallQueue` reads `getPriorityLevel()` to choose a subqueue.

## State and persistence behavior

The interface has no state. Implementations carry per-call user, caller context, and priority metadata in memory.

## Dependencies and integration points

It depends on `UserGroupInformation` and optional `CallerContext`. It is implemented by server calls and by scheduler test/dummy objects.

## Risks and test signals

Callers must not assume `getCallerContext()` is always supported. Tests should cover UGI extraction, priority propagation into `FairCallQueue`, and fallback behavior for schedulable implementations that only provide UGI and priority.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Schedulable.java -->

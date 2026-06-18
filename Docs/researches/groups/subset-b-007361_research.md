# subset-b-007361 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/FairCallQueue.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/FairCallQueue.java

## Purpose
`FairCallQueue` is Hadoop IPC's multi-priority `BlockingQueue` implementation for server calls. It partitions total capacity across per-priority `LinkedBlockingQueue` instances, uses a `RpcMultiplexer` to select dequeue priority, and exports queue-size and overflow metrics through a per-namespace MBean/metrics source.

## Important APIs, Types, and Functions
Constructors allocate weighted subqueues and install `WeightedRoundRobinMultiplexer`. `add`, `put`, `offer`, `take`, `poll`, `peek`, `drainTo`, `remainingCapacity`, `getQueueSizes`, and `getOverflowedCalls` implement the queue contract. `MetricsProxy` implements `FairCallQueueMXBean` and `MetricsSource`, tracks delegate revisions, and avoids retaining retired queues with a `WeakReference`.

## Control Flow
Enqueue paths read `Schedulable.getPriorityLevel()`. `add` and `put` can overflow into lower-priority queues; `offer` only targets the assigned queue. Successful insertions release a semaphore permit. Consumers acquire a permit before `removeNextElement`, then poll the multiplexer-selected queue and scan all queues if races left that queue empty. Overflow behavior maps to `CallQueueOverflowException` variants, optionally failover when server failover is enabled.

## State and Persistence Behavior
State is in-memory only: subqueue contents, semaphore permits, overflow counters, multiplexer cursor, and metrics delegate. Correctness depends on keeping semaphore permits synchronized with actual queued elements. Metrics registration is global per namespace and revisions distinguish queue replacement.

## Dependencies and Integration Points
It depends on `Schedulable`, `RpcMultiplexer`, `WeightedRoundRobinMultiplexer`, `CallQueueManager`, Hadoop metrics/MBeans, and server call scheduling. `TestFairCallQueue` covers capacity distribution, queue operations, blocking semantics, overflow counters, MBean, and metrics signals.

## Risks and Test Signals
Risks include semaphore/subqueue skew, starvation if multiplexer behavior changes, priority overflow policy mistakes, and stale metrics delegates. Tests should stress concurrent producers/consumers, `drainTo`, failover-enabled overflow, weighted capacity residue, and replacement of queues under one metrics namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/FairCallQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/FairCallQueueMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/FairCallQueueMXBean.java

## Purpose
This interface is the JMX management contract for `FairCallQueue`. It exposes per-priority queue size, per-priority overflow counters, and a revision counter for detecting queue replacement.

## Important APIs, Types, and Functions
`getQueueSizes()` returns an array indexed by priority level. `getOverflowedCalls()` returns the accumulated overflow count for each subqueue. `getRevision()` is incremented by `FairCallQueue.MetricsProxy` whenever a new queue delegate is installed for the namespace.

## Control Flow
There is no implementation flow in this file. Calls are served by `FairCallQueue.MetricsProxy`, which resolves the current queue through a weak reference and returns empty arrays if no live delegate remains.

## State and Persistence Behavior
The interface declares no state. Runtime state comes from the implementing metrics proxy and underlying `FairCallQueue`.

## Dependencies and Integration Points
It is registered as `Hadoop:service=<ns>,name=FairCallQueue` by `MBeans.register` and feeds Hadoop metrics records. `TestFairCallQueue` validates MBean access and metrics values.

## Risks and Test Signals
The main compatibility risk is changing array ordering or semantics. Tests should verify the exposed arrays match subqueue priority order and that `getRevision` changes after queue replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/FairCallQueueMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/GenericRefreshProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/GenericRefreshProtocol.java

## Purpose
`GenericRefreshProtocol` defines the RPC interface for refreshing arbitrary runtime resources by string identifier. It is used for administrative refresh commands whose targets are registered dynamically rather than hard-coded as separate protocols.

## Important APIs, Types, and Functions
The protocol has `versionID = 1L` and one idempotent method, `refresh(String identifier, String[] args)`, returning a `Collection<RefreshResponse>`. `@KerberosInfo` binds server principal lookup to the standard Hadoop service user key.

## Control Flow
Clients call `refresh`; server-side translators typically dispatch to `RefreshRegistry`, which locates one or more `RefreshHandler` implementations for the identifier and returns one response per handler.

## State and Persistence Behavior
The protocol has no state and persists nothing. Effects are delegated to handlers, which may reload in-memory configuration or other runtime resources.

## Dependencies and Integration Points
It integrates with Hadoop RPC, Kerberos service-principal resolution, retry annotations via `@Idempotent`, `RefreshRegistry`, `RefreshHandler`, and `RefreshResponse`.

## Risks and Test Signals
Risks are handler-specific side effects despite the idempotent annotation, ambiguous identifiers, and security exposure if refresh endpoints are over-broad. Tests should cover valid and invalid identifiers, multiple handlers, and permission/authentication paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/GenericRefreshProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/IdentityProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/IdentityProvider.java

## Purpose
`IdentityProvider` is a small scheduling extension point. It converts a `Schedulable` RPC call into a string identity used by schedulers to group or rate callers.

## Important APIs, Types, and Functions
The single method, `makeIdentity(Schedulable obj)`, returns an identity string or `null` when no identity can be built. Implementations may use `Schedulable.getUserGroupInformation()` and `getCallerContext()`.

## Control Flow
There is no implementation in this file. Scheduler implementations call an `IdentityProvider` when attributing costs or determining priority/backoff.

## State and Persistence Behavior
The interface declares no state. Implementations should be side-effect free because they run in the RPC scheduling path.

## Dependencies and Integration Points
It depends on `Schedulable` and is consumed by RPC scheduler implementations such as decay or cost-based schedulers elsewhere in the IPC package.

## Risks and Test Signals
Risks include returning unstable identities, throwing from optional `CallerContext` access, or leaking sensitive user context into metrics/logs. Scheduler tests should exercise UGI-only and caller-context identity providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/IdentityProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/IpcException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/IpcException.java

## Purpose
`IpcException` is a minimal checked exception for IPC-layer failures where an IPC connection cannot be established.

## Important APIs, Types, and Functions
It extends `IOException`, defines `serialVersionUID = 1L`, and exposes a single string-message constructor.

## Control Flow
There is no special control flow. Callers throw it to distinguish low-level IPC connection setup failures from service-side RPC errors.

## State and Persistence Behavior
Only the inherited exception message/cause state exists. Nothing is persisted.

## Dependencies and Integration Points
It integrates with Hadoop client/server connection code through the common `IOException` path.

## Risks and Test Signals
The risk is mostly semantic: callers may overuse this generic type and lose detailed diagnostics. Tests should verify connection-failure paths preserve the original message and are handled as IO failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/IpcException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ObserverRetryOnActiveException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ObserverRetryOnActiveException.java

## Purpose
This exception tells HDFS observer clients that a request failed on an ObserverNode and should be retried against the active NameNode directly rather than cycling through other observers.

## Important APIs, Types, and Functions
It extends `StandbyException`, is private/evolving, has `serialVersionUID = 1L`, and provides a single message constructor.

## Control Flow
Server-side observer code throws this when observer retry is inappropriate. Client retry policy detects the remote exception class and redirects to the active endpoint.

## State and Persistence Behavior
Only exception message state is stored. It has no persistence role.

## Dependencies and Integration Points
It depends on `StandbyException` and integrates with HDFS observer read retry/failover handling through Hadoop RPC remote exception wrapping.

## Risks and Test Signals
Risks are class-name compatibility across remote exception unwrapping and incorrect retry policy interpretation. Tests should cover wrapping/unwrapping through `RemoteException` and active-only retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ObserverRetryOnActiveException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProcessingDetails.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProcessingDetails.java

## Purpose
`ProcessingDetails` records per-RPC timing breakdowns and response status for queueing, handling, processing, locking, and response phases. It supports metrics, logging, scheduler feedback, and deferred-response accounting.

## Important APIs, Types, and Functions
The `Timing` enum covers `ENQUEUE`, `QUEUE`, `HANDLER`, `PROCESSING`, `LOCKFREE`, `LOCKWAIT`, `LOCKSHARED`, `LOCKEXCLUSIVE`, and `RESPONSE`. `get`, `set`, and `add` convert values through the instance `TimeUnit`. `setReturnStatus` and `getReturnStatus` track `RpcStatusProto`.

## Control Flow
Callers create a details object with a base unit, increment or set phase timings as an RPC moves through the server, then consume values for metrics. Negative values are clamped to zero on read to hide rare `nanoTime` regressions. Protobuf deferred callbacks update processing and lock-free time before setting the deferred response/error.

## State and Persistence Behavior
State is per-call and in-memory. No durable persistence is performed.

## Dependencies and Integration Points
It depends on protobuf RPC status enums and is used by `Server.Call`, `RpcScheduler.addResponseTime`, weighted cost providers, and tests such as `TestProcessingDetails`, `TestDecayRpcScheduler`, and `TestWeightedTimeCostProvider`.

## Risks and Test Signals
Risks include unit-conversion mistakes, overflow/truncation when schedulers cast to int, and inconsistent `PROCESSING` vs lock component accounting. Tests should assert conversions, `toString` format, negative clamping, and scheduler cost calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProcessingDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufHelper.java

## Purpose
`ProtobufHelper` is a deprecated compatibility facade for protobuf-related IPC helpers. It delegates shaded protobuf operations to `ShadedProtobufHelper` while retaining legacy unshaded `com.google.protobuf.ServiceException` handling.

## Important APIs, Types, and Functions
`getRemoteException(ServiceException)` delegates to shaded helper. The overloaded deprecated unshaded version extracts an `IOException` cause or wraps the service exception. ByteString helpers and token conversion helpers (`tokenFromProto`, `protoFromToken`) also delegate.

## Control Flow
All modern paths are pass-through. Legacy exception extraction checks the cause for null and `IOException` type before returning or wrapping.

## State and Persistence Behavior
The class has no state. Token conversion creates protobuf representations of token fields but does not persist them.

## Dependencies and Integration Points
It depends on shaded protobuf helper APIs, Hadoop `Token`, `TokenProto`, and legacy protobuf classes. External applications may still call it, but Hadoop internals should not.

## Risks and Test Signals
The key risk is runtime dependency on unshaded protobuf 2.5 for deprecated APIs. Tests should cover shaded and unshaded service exceptions, empty byte arrays, fixed strings, and token round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngine.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngine.java

## Purpose
`ProtobufRpcEngine` is the deprecated RPC engine for unshaded protobuf 2.5 clients. It remains for compatibility while server dispatch is implemented by `ProtobufRpcEngine2` and can handle legacy unshaded service implementations.

## Important APIs, Types, and Functions
`getProxy` overloads create dynamic proxies backed by `Invoker`. `Invoker.invoke` validates protobuf RPC arguments, builds `RpcProtobufRequest`, calls `Client.call`, supports asynchronous mode through `ASYNC_RETURN_MESSAGE`, and decodes return messages by cached default instances. The nested `Server` extends `ProtobufRpcEngine2.Server` and provides legacy callback registration and `processCall` for unshaded `BlockingService`.

## Control Flow
Client calls enter the dynamic proxy, wrap method/header plus payload, trace/log the call, and decode the returned `RpcWritable.Buffer`. Server compatibility dispatch looks up the protobuf method descriptor, decodes the request payload, invokes `callBlockingMethod`, handles deferred callback registration, and maps `ServiceException` causes back to server exceptions.

## State and Persistence Behavior
State includes the static `ClientCache`, per-invoker return prototype cache, connection id, fallback/auth flags, and thread-local async/deferred callback state. It persists nothing.

## Dependencies and Integration Points
It uses legacy `com.google.protobuf`, Hadoop `Client`, `RpcWritable`, `RPC.Server`, tracing, and `ProtobufRpcEngine2` registration. Tests in protobuf RPC compatibility and handoff suites exercise both old and new paths.

## Risks and Test Signals
Risks include classpath dependence on unshaded protobuf, thread-local callback leakage, incorrect async return handling, and compatibility drift with `ProtobufRpcEngine2`. Tests should cover old client/new server interoperability, deferred responses, error unwrapping, async mode, and client cache cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngine2.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngine2.java

## Purpose
`ProtobufRpcEngine2` is the primary shaded-protobuf Hadoop RPC engine. It creates protobuf client proxies, registers the protobuf RPC request deserializer, builds RPC servers, dispatches server calls to shaded or legacy protobuf services, and supports asynchronous/deferred responses.

## Important APIs, Types, and Functions
`registerProtocolEngine` binds `RPC_PROTOCOL_BUFFER` to `RpcProtobufRequest` and `ProtoBufRpcInvoker`. `Invoker` implements client proxy invocation and return decoding. `Server` extends `RPC.Server`, registers protocol implementations, exposes `registerForDeferredResponse2`, and owns `CURRENT_CALLBACK`/`CURRENT_CALL_INFO`. `ProtoBufRpcInvoker` validates protocol/version, finds method descriptors, decodes requests, invokes `BlockingService`, and wraps responses with `RpcWritable`.

## Control Flow
Client proxy calls require `(RpcController, Message)` arguments, build `RequestHeaderProto`, call `Client.call`, and either set a thread-local `AsyncGet` or decode the response immediately. Server calls decode the request header, select the declaring protocol and client version, reject unknown protocols or versions, then dispatch to shaded `BlockingService` or `ProtobufRpcEngine.Server.processCall` for unshaded legacy services. Deferred responses mark the current server call and return null until callback completion.

## State and Persistence Behavior
State is runtime only: static client cache, return prototype caches, connection ids, auth fallback flags, alignment context, and thread-local async/deferred call data. No persistent data is written.

## Dependencies and Integration Points
It integrates with `RPC`, `Client`, `RpcWritable`, `ProtocolMetaInfoPB`, shaded protobuf, legacy engine compatibility, tracing, SASL/security setup via higher `RPC` methods, and server metrics. Tests include `TestProtoBufRpc`, `TestProtoBufRpcServerHandoff`, `TestProtoBufRPCCompatibility`, and `TestRPC`.

## Risks and Test Signals
High-risk areas are protocol-version lookup, legacy/shaded service branching, thread-local cleanup, method-name uniqueness, async response decoding, and deferred metrics timing. Tests should cover unknown method/protocol, version mismatch, shaded and unshaded services, async mode, deferred success/error, and client cache clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngine2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngineCallback.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngineCallback.java

## Purpose
This deprecated callback interface lets legacy unshaded protobuf RPC server implementations complete a response asynchronously after registering for a deferred response.

## Important APIs, Types, and Functions
`setResponse(com.google.protobuf.Message message)` supplies the eventual protobuf response. `error(Throwable t)` completes the deferred RPC with an error.

## Control Flow
Server code calls `ProtobufRpcEngine.Server.registerForDeferredResponse`, returns from the service method, and later invokes one callback method. The engine marks the call as deferred and updates response/error plus metrics when callback fires.

## State and Persistence Behavior
The interface carries no state. Implementations capture the current RPC server call and method name in runtime memory.

## Dependencies and Integration Points
It depends on unshaded protobuf and is superseded by `ProtobufRpcEngineCallback2`. It integrates with `ProtobufRpcEngine.Server`.

## Risks and Test Signals
Risks are callback invocation after request context is gone, double completion, and legacy protobuf classpath issues. Handoff/deferred-response tests should include success and error callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngineCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngineCallback2.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngineCallback2.java

## Purpose
`ProtobufRpcEngineCallback2` is the shaded-protobuf deferred response callback for `ProtobufRpcEngine2` server implementations.

## Important APIs, Types, and Functions
It declares `setResponse(org.apache.hadoop.thirdparty.protobuf.Message message)` and `error(Throwable t)`.

## Control Flow
Server code obtains an implementation from `ProtobufRpcEngine2.Server.registerForDeferredResponse2`, returns control to the RPC engine, and later completes the call through the callback.

## State and Persistence Behavior
No state is declared here. Runtime implementation state captures the active `Call`, `RPC.Server`, and method name.

## Dependencies and Integration Points
It depends on Hadoop's shaded protobuf package and integrates with `ProtobufRpcEngine2.Server` deferred handling and metrics.

## Risks and Test Signals
Risks include failure to call exactly one completion method and thread-local callback leakage. Tests should cover deferred success/error, metrics update, and callback use from another thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngineCallback2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufWrapperLegacy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufWrapperLegacy.java

## Purpose
`ProtobufWrapperLegacy` adapts unshaded `com.google.protobuf.Message` instances to `RpcWritable`, isolating legacy protobuf references from most of the RPC codebase and allowing runtime absence when legacy messages are not used.

## Important APIs, Types, and Functions
The constructor validates payloads through `isUnshadedProtobufMessage`. `writeTo` writes a delimited protobuf into `ResponseBuffer`. `readFrom` parses a delimited message from a byte-array-backed `ByteBuffer`. `PROTOBUF_KNOWN_NOT_FOUND` avoids repeated class loading failures.

## Control Flow
Wrapping first checks class availability and assignability. Serialization precomputes delimited size and ensures response buffer capacity. Deserialization reads the varint length, pushes a coded-input limit, parses through the message parser, checks the final tag, and advances the source buffer by consumed bytes.

## State and Persistence Behavior
State is the current legacy protobuf message and the static classpath-absence flag. No persistence is performed.

## Dependencies and Integration Points
It is used by `RpcWritable.wrap` and legacy protobuf server/client compatibility paths in `ProtobufRpcEngine` and `ProtobufRpcEngine2`.

## Risks and Test Signals
Risks include byte-buffer array assumptions, parser limit mistakes, stale classpath absence caching in exotic classloader scenarios, and legacy dependency drift. Tests should verify wrap detection with and without unshaded protobuf, round-trip serialization, and buffer position advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufWrapperLegacy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolInfo.java

## Purpose
`ProtocolInfo` is a runtime-retained annotation that overrides the default RPC protocol name and optionally declares a protocol version.

## Important APIs, Types, and Functions
`protocolName()` is required. `protocolVersion()` defaults to `-1`, which tells `RPC.getProtocolVersion` to fall back to the legacy `versionID` field.

## Control Flow
`RPC.getProtocolName` and `RPC.getProtocolVersion` inspect this annotation when registering protocols and constructing client request headers.

## State and Persistence Behavior
Annotation metadata is stored in class metadata at runtime. It persists nothing dynamically.

## Dependencies and Integration Points
It is used by protobuf protocol interfaces such as `ProtocolMetaInfoPB` and by server registration/version matching.

## Risks and Test Signals
Risks include mismatched annotation names between client/server translators and missing versions causing reflection failures. Compatibility tests should cover annotated and legacy `versionID` protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInfoPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInfoPB.java

## Purpose
`ProtocolMetaInfoPB` is the protobuf RPC protocol used to ask a server which protocol versions and method signatures it supports.

## Important APIs, Types, and Functions
It extends `ProtocolInfoService.BlockingInterface` and is annotated with protocol name `org.apache.hadoop.ipc.ProtocolMetaInfoPB` and version `1`.

## Control Flow
`RPC.Server.initProtocolMetaInfo` registers this protocol on every RPC server through a `ProtocolMetaInfoServerSideTranslatorPB`. Clients use `RpcClientUtil` to reuse an existing connection and query method support.

## State and Persistence Behavior
The interface has no state. Responses are derived from the server's registered protocol map.

## Dependencies and Integration Points
It depends on generated `ProtocolInfoProtos` and integrates with `ProtobufRpcEngine2`.

## Risks and Test Signals
Risks are annotation drift and generated proto incompatibility. Tests should verify method support queries across multiple protocols and versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInfoPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInfoServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInfoServerSideTranslatorPB.java

## Purpose
This translator implements the `ProtocolMetaInfoPB` service by reading the server's registered protocol/version map and returning supported versions or method signatures.

## Important APIs, Types, and Functions
`getProtocolVersions` iterates all `RPC.RpcKind` values and emits version lists. `getProtocolSignature` returns method fingerprints for each version of a requested protocol/rpc kind. `getProtocolVersionForRpcKind` loads the protocol class, resolves annotated protocol name, and asks `RPC.Server.getSupportedProtocolVersions`.

## Control Flow
Requests contain class names and rpc kind strings. The translator reflects the class, converts rpc kind names through `RPC.RpcKind.valueOf`, collects versions, and builds protobuf responses. Missing registrations produce empty responses; class loading failures become `ServiceException`.

## State and Persistence Behavior
It stores only a reference to the live `RPC.Server`. No state is persisted.

## Dependencies and Integration Points
It depends on generated `ProtocolInfoProtos`, `ProtocolSignature`, `RPC.Server.VerProtocolImpl`, and shaded protobuf service exception handling. It is registered automatically by `RPC.Server`.

## Risks and Test Signals
Risks include accepting arbitrary class names for reflection, enum value errors, and stale protocol maps after dynamic registration. Tests should cover missing protocol, version lists across rpc kinds, class-not-found, and signature contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInfoServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInterface.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInterface.java

## Purpose
`ProtocolMetaInterface` is implemented by client-side protocol translators that can report whether a server supports a method.

## Important APIs, Types, and Functions
The single API is `isMethodSupported(String methodName)`, returning a boolean and throwing `IOException` for RPC or lookup failures.

## Control Flow
Implementations usually delegate to `RpcClientUtil.isMethodSupported`, which queries the server's `ProtocolMetaInfoPB` service and caches signatures.

## State and Persistence Behavior
The interface has no state. Implementations may cache server method signatures in memory.

## Dependencies and Integration Points
It integrates with generated client translators for Hadoop services and with `RpcClientUtil`/`ProtocolMetaInfoPB`.

## Risks and Test Signals
Risks include assuming method names are unique and stale caches after server upgrades. Tests should cover positive and negative method support checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolProxy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolProxy.java

## Purpose
`ProtocolProxy` wraps a client proxy with optional server-method support discovery for versioned protocols.

## Important APIs, Types, and Functions
The constructor stores the protocol class, proxy, and `supportServerMethodCheck` flag. `getProxy` returns the underlying proxy. `isMethodSupported` lazily calls `fetchServerMethods`, compares protocol versions, and checks method fingerprints through `ProtocolSignature`.

## Control Flow
If server-method checking is disabled, every method is treated as supported. Otherwise the first support check reflects the client method, calls `VersionedProtocol.getProtocolSignature` through the proxy, detects version mismatch, caches server method hashes, and evaluates requested method hashes.

## State and Persistence Behavior
State is in-memory per proxy: fetched flag and optional hash set. No persistence is performed.

## Dependencies and Integration Points
It depends on `VersionedProtocol`, `RPC`, and `ProtocolSignature`. Protobuf engine proxies currently pass `false`, while legacy/versioned clients may use checks.

## Risks and Test Signals
Risks include method-name/parameter mismatch, stale cached signatures, and casts to `VersionedProtocol`. Compatibility tests should cover matching signatures, partial method sets, and version mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolSignature.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolSignature.java

## Purpose
`ProtocolSignature` serializes a protocol version and method fingerprint list. It underpins Hadoop RPC compatibility checks and method-support queries.

## Important APIs, Types, and Functions
It implements `Writable`, registers a factory, stores `version` and nullable `methods`, and provides `getFingerprint(Method)`, `getFingerprint(Method[])`, `getProtocolSignature(...)`, and `resetCache`. A null methods array means client and server protocol methods match.

## Control Flow
Fingerprints hash method name, return type, and parameter type names. Method arrays are converted to fingerprints, sorted, and hashed for order-independent comparison. Static cache maps protocol names to signatures/fingerprints and is synchronized.

## State and Persistence Behavior
Writable read/write serializes version plus optional method hashes. Static cache stores reflected signatures in memory only.

## Dependencies and Integration Points
It is used by `VersionedProtocol`, `ProtocolProxy`, `RpcClientUtil`, and `ProtocolMetaInfoServerSideTranslatorPB`. `TestRPCCompatibility` exercises fingerprint and cache behavior.

## Risks and Test Signals
Risks include hash collisions, cache key ignoring version differences for same protocol name, and `Arrays.sort` mutating input arrays. Tests should verify order independence, method overload distinctions, cache reset, and version mismatch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolSignature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolTranslator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolTranslator.java

## Purpose
`ProtocolTranslator` marks client-side translators that wrap an underlying RPC proxy and can expose that proxy for connection and lifecycle operations.

## Important APIs, Types, and Functions
`getUnderlyingProxyObject()` returns the real dynamic proxy object.

## Control Flow
`RPC.getConnectionIdForProxy` checks this interface and unwraps translators before reading the `RpcInvocationHandler`.

## State and Persistence Behavior
The interface has no state. Implementations hold whatever proxy state they wrap.

## Dependencies and Integration Points
It integrates with translator classes generated or hand-written around protobuf services, and with `RPC.stopProxy`/connection-id helper paths.

## Risks and Test Signals
Risks include returning the wrong object or a non-RPC proxy, breaking connection reuse and protocol metadata queries. Tests should cover translator unwrapping and proxy shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolTranslator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProxyCombiner.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProxyCombiner.java

## Purpose
`ProxyCombiner` builds one dynamic proxy for an interface whose methods are implemented by multiple underlying protocol proxies.

## Important APIs, Types, and Functions
`combine(Class<T>, Object... proxies)` verifies method coverage, then returns a proxy backed by `CombinedProxyInvocationHandler`. The handler implements `RpcInvocationHandler`, delegates calls, returns the first proxy's connection id, formats `toString`, and closes all closeable delegates with `MultipleIOException`.

## Control Flow
Build-time coverage scans every method in the combined interface against delegate classes. Invocation loops through delegates and calls `Method.invoke`; target exceptions are unwrapped. Close loops through delegates and accumulates IO failures.

## State and Persistence Behavior
State is only the combined interface and delegate proxy array. No persistence is performed.

## Dependencies and Integration Points
It depends on Java dynamic proxies, `RpcInvocationHandler`, `RPC.getConnectionIdForProxy`, Guava `Joiner`, and `MultipleIOException`.

## Risks and Test Signals
Risks include invoking a method on a delegate that does not implement it after only partial reflective checking, ambiguous duplicate methods choosing the first proxy, and assuming all connection ids match. Tests should cover complete/incomplete method coverage, duplicate methods, exception propagation, and close aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProxyCombiner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RPC.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RPC.java

## Purpose
`RPC` is the central facade for Hadoop IPC. It defines RPC kinds, protocol naming/versioning helpers, client proxy construction, proxy shutdown, server construction, version mismatch exceptions, and the `RPC.Server` base that maps protocol/version pairs to implementations.

## Important APIs, Types, and Functions
`RpcKind` encodes builtin/writable/protobuf wire kinds. `setProtocolEngine` and `getProtocolEngine` configure cached `RpcEngine` instances. Many `getProxy`, `getProtocolProxy`, and `waitForProtocolProxy` overloads create clients with UGI, socket factory, timeout, retry policy, auth fallback, and alignment context. `Builder` builds servers. `Server` registers protocol implementations, installs `ProtocolMetaInfoPB`, resolves supported versions, and dispatches calls to rpc-kind invokers.

## Control Flow
Client construction initializes SASL when security is enabled, resolves the configured engine, and delegates proxy creation. `waitForProtocolProxy` retries connection failures until timeout or interruption. Server construction validates mandatory builder fields, delegates to the protocol engine, registers protocol implementation maps, and installs protocol metadata service. Incoming calls are dispatched by `Server.call` through the registered invoker for the request kind.

## State and Persistence Behavior
Static `PROTOCOL_ENGINES` caches one engine per protocol class. Server instances hold per-rpc-kind protocol implementation maps keyed by protocol name and version, plus scheduler priority side effects for service principals. No durable persistence occurs.

## Dependencies and Integration Points
It integrates with `Client`, `Server`, `RpcEngine`, `ProtobufRpcEngine2`, SASL/security, UGI, Hadoop configuration, protocol metadata, retry policies, and service-specific translators. `TestRPC`, `TestRPCWaitForProxy`, `TestMultipleProtocolServer`, and compatibility tests cover major paths.

## Risks and Test Signals
High-risk areas are engine cache lifetime/config drift, protocol annotation/version fallback, security initialization, proxy close semantics, server registration maps, and wait-loop timeout arithmetic. Tests should cover multiple protocols, version mismatch, unauthorized access, proxy stop failures, security-enabled clients, and metadata service registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RPC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshCallQueueProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshCallQueueProtocol.java

## Purpose
`RefreshCallQueueProtocol` defines the administrative RPC used by HDFS-facing services to reload or replace the active RPC call queue at runtime.

## Important APIs, Types, and Functions
It declares `versionID = 1L` and one idempotent method, `refreshCallQueue()`, which throws `IOException`.

## Control Flow
Clients invoke the method on a server endpoint; the server implementation performs queue-manager refresh logic outside this interface.

## State and Persistence Behavior
The interface has no state. Implementations mutate in-memory server call-queue configuration rather than persistent data.

## Dependencies and Integration Points
It uses standard Hadoop Kerberos service principal annotations and integrates with `CallQueueManager`, `FairCallQueue`, and administrative refresh commands.

## Risks and Test Signals
Risks include disrupting live calls during queue replacement and mislabeling non-idempotent refresh side effects. Tests should cover refresh under load and MBean/metrics revision changes after replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshCallQueueProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshHandler.java

## Purpose
`RefreshHandler` is the plugin interface for runtime refresh actions registered in `RefreshRegistry`.

## Important APIs, Types, and Functions
`handleRefresh(String identifier, String[] args)` returns a `RefreshResponse` describing success/failure and user-facing status.

## Control Flow
`RefreshRegistry.dispatch` calls every handler registered under an identifier, catches exceptions, and records one response per handler.

## State and Persistence Behavior
The interface declares no state. Implementations may reload in-memory configuration or external resources.

## Dependencies and Integration Points
It integrates with `RefreshRegistry`, `GenericRefreshProtocol`, and service-specific refresh implementations.

## Risks and Test Signals
Risks include null responses, thrown runtime exceptions, and handlers retaining resources after registration. Registry tests should cover success, failure, null response handling, and unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshRegistry.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshRegistry.java

## Purpose
`RefreshRegistry` is the in-memory registry that maps refresh identifiers to one or more `RefreshHandler` implementations and dispatches administrative refresh calls.

## Important APIs, Types, and Functions
`defaultRegistry` returns the singleton. `register`, `unregister`, and `unregisterAll` mutate the handler multimap. `dispatch` validates the identifier, invokes handlers, logs responses, wraps handler exceptions as failed `RefreshResponse` objects, and stamps sender names.

## Control Flow
All public registry operations are synchronized. `dispatch` gets handlers for the identifier, fails with valid option names when none exist, iterates handlers, enforces non-null responses, catches exceptions, and returns the collected responses.

## State and Persistence Behavior
State is the `HashMultimap<String, RefreshHandler>` and singleton holder. Registration prevents handler GC until unregistered. There is no durable persistence.

## Dependencies and Integration Points
It depends on shaded Guava `HashMultimap`/`Joiner`, `RefreshHandler`, `RefreshResponse`, and logging. It is a likely backend for `GenericRefreshProtocol` implementations.

## Risks and Test Signals
Risks include memory leaks from forgotten unregisters, synchronized handler execution blocking other refresh operations, and exposing handler class names. Tests should cover multiple handlers, missing identifiers, exception wrapping, null response handling, and unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshResponse.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshResponse.java

## Purpose
`RefreshResponse` is the status object returned by refresh handlers, carrying an exit code, message, and optional sender name.

## Important APIs, Types, and Functions
`successResponse()` returns code `0` and message `Success`. The constructor sets return code and message. Getters/setters expose `senderName`, `returnCode`, and `message`. `toString` formats optional sender, message, and exit code.

## Control Flow
Handlers create or mutate responses. `RefreshRegistry.dispatch` sets sender names before returning responses.

## State and Persistence Behavior
It is a mutable in-memory value object. No persistence is performed.

## Dependencies and Integration Points
It is used by `RefreshHandler` and `GenericRefreshProtocol`.

## Risks and Test Signals
Risks are null messages, mutable responses being shared, and consumers treating nonzero codes inconsistently. Tests should cover string formatting with and without sender/message and success/failure codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RemoteException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RemoteException.java

## Purpose
`RemoteException` wraps an exception thrown by the remote RPC server, preserving the remote class name, message, and optional protobuf RPC error code for client-side unwrapping.

## Important APIs, Types, and Functions
Constructors accept class name, message, and optional `RpcErrorCodeProto`. `getClassName` and `getErrorCode` expose metadata. `unwrapRemoteException` variants instantiate matching `IOException` classes through a string constructor and set this wrapper as cause. `valueOf(Attributes)` builds from XML attributes.

## Control Flow
Clients catch `RemoteException`, optionally match known classes, and unwrap. Reflection failures return the wrapper unchanged. Error code `-1` represents unspecified or newer protobuf errors.

## State and Persistence Behavior
State is exception metadata only. It may be serialized through normal exception/RPC mechanisms but persists nothing itself.

## Dependencies and Integration Points
It integrates with RPC response headers, protobuf engines, SASL/RPC tests, and service clients that unwrap server exceptions.

## Risks and Test Signals
Risks include class-name compatibility, missing string constructors, reflection access, and unknown error-code numbers. Tests should cover unwrap success/failure, lookup filtering, XML construction, and `ServiceException` cause chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RemoteException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ResponseBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ResponseBuffer.java

## Purpose
`ResponseBuffer` is a byte-length-framed `DataOutputStream` used to encode RPC responses with a four-byte length prefix.

## Important APIs, Types, and Functions
Constructors allocate a `FramedBuffer`. `writeTo`, `toByteArray`, `capacity`, `setCapacity`, `ensureCapacity`, and `reset` manage the buffer. `FramedBuffer` reserves four framing bytes, overrides `size`, writes big-endian length in `setSize`, and resets count to the frame offset.

## Control Flow
Writers append response payload through `DataOutputStream`. Before extraction, `getFramedBuffer` updates the first four bytes from `written`. `ensureCapacity` grows the backing array for protobuf serialization.

## State and Persistence Behavior
State is a reusable in-memory byte array plus `written` count. It does not persist data.

## Dependencies and Integration Points
It is used by `RpcWritable.writeTo`, protobuf wrappers, server responder code, and tests such as `TestResponseBuffer` and `TestIPCServerResponder`.

## Risks and Test Signals
Risks include incorrect frame length after reset/reuse, capacity shrink/expand bugs, and mismatch between `written` and buffer count. Tests should verify framing bytes, reset behavior, capacity changes, and response writes of varied sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ResponseBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RetriableException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RetriableException.java

## Purpose
`RetriableException` signals a temporary server condition where clients may retry, such as startup or transient unavailability.

## Important APIs, Types, and Functions
It extends `IOException`, has constructors from `Exception` and `String`, and is marked evolving.

## Control Flow
Server code throws it; RPC wraps it remotely; client retry policies inspect the class name after `RemoteException` unwrapping and decide whether to retry.

## State and Persistence Behavior
Only normal exception state exists. It persists nothing.

## Dependencies and Integration Points
It integrates with Hadoop retry policies and RPC remote exception handling.

## Risks and Test Signals
Risks include retry storms if thrown for non-transient conditions and lost cause type when using the string constructor. Tests should cover retry policy classification and remote unwrap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RetriableException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RetryCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RetryCache.java

## Purpose
`RetryCache` deduplicates retried non-idempotent RPC requests on the server by client UUID and call id, allowing successful prior responses or payloads to be reused.

## Important APIs, Types, and Functions
`CacheEntry` tracks UUID, call id, expiration, and state (`INPROGRESS`, `SUCCESS`, `FAILED`). `CacheEntryWithPayload` stores a response payload. Public/static APIs include `waitForCompletion`, `setState`, `addCacheEntry`, `addCacheEntryWithPayload`, `clear`, metric accessors, and explicit `lock`/`unlock`.

## Control Flow
`waitForCompletion` skips non-RPC, invalid call ids, and dummy client ids. Otherwise it locks the cache, inserts a new in-progress entry or finds an existing one. If existing, callers wait until completion; success returns the previous entry, while failure resets state to in-progress so the caller retries work. Completion notifies waiters.

## State and Persistence Behavior
State is a `LightWeightCache` with expiration, lock, cache name, and metrics. It is in-memory but can be repopulated from edit logs through `addCacheEntry*`, treating loaded entries as successful.

## Dependencies and Integration Points
It depends on `ClientId`, `Server.isRpcInvocation`, `RpcConstants`, lightweight Hadoop cache collections, and `RetryCacheMetrics`. HDFS NameNode operations use it for at-most-once semantics. `TestRetryCache` and `TestRetryCacheMetrics` are direct signals.

## Risks and Test Signals
Risks include UUID length validation, wait interruption handling that continues waiting, payload mutation races, expiration of still-needed results, and forgetting `setState` after work. Tests should cover concurrent retries, failed first attempts, payload reuse, skip conditions, edit-log reload, expiration, and metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RetryCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcClientException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcClientException.java

## Purpose
`RpcClientException` is the RPC exception subclass for client-side RPC execution failures.

## Important APIs, Types, and Functions
It extends `RpcException`, defines `serialVersionUID = 1L`, and has package-private constructors for message and message-plus-cause.

## Control Flow
Client internals throw it where failures should remain distinguishable from server-side `RpcServerException`.

## State and Persistence Behavior
Only exception message/cause state exists. No persistence occurs.

## Dependencies and Integration Points
It fits into the `RpcException` hierarchy used by Hadoop client transport code.

## Risks and Test Signals
Risks include package-private constructors limiting use outside IPC and losing specific transport failure detail. Tests should verify response-header mapping where client exceptions are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcClientException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcClientUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcClientUtil.java

## Purpose
`RpcClientUtil` provides client-side helper logic for method-support discovery through the protocol metadata service and for concise RPC tracing names.

## Important APIs, Types, and Functions
`isMethodSupported` caches protocol signatures by server address, protocol, and rpc kind. `ProtoSigCacheKey` defines cache identity. `convertProtocolSignatureProtos` converts protobuf signature lists to `ProtocolSignature` maps. `methodToTraceString(Method)` builds `OuterClass#method` style names.

## Control Flow
On cache miss, `isMethodSupported` creates a minimal configuration, sets the metadata engine to `ProtobufRpcEngine2`, obtains a `ProtocolMetaInfoPB` proxy reusing the original connection id, fetches signatures, and caches them. It then finds the named client method and compares its fingerprint against the version map.

## State and Persistence Behavior
Static `signatureMap` caches signatures for process lifetime. No persistence is written.

## Dependencies and Integration Points
It depends on `RPC`, `ProtocolMetaInfoPB`, `ProtocolSignature`, protobuf metadata protos, `NetUtils`, and `ShadedProtobufHelper.ipc`. It is used by protocol translators and tracing in protobuf engines.

## Risks and Test Signals
Risks include stale cache after server restart/upgrade, assuming unique method names, cache key equality null assumptions, and security concerns from metadata proxy connection reuse. Tests should cover cache hit/miss, missing methods, multiple versions, and trace string formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcClientUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcConstants.java

## Purpose
`RpcConstants` centralizes wire-level Hadoop RPC constants: special call ids, dummy client id, retry sentinel, header bytes, header length, and protocol version.

## Important APIs, Types, and Functions
Constants include `AUTHORIZATION_FAILED_CALL_ID`, `INVALID_CALL_ID`, `CONNECTION_CONTEXT_CALL_ID`, `PING_CALL_ID`, `DUMMY_CLIENT_ID`, `INVALID_RETRY_COUNT`, `HEADER` (`hrpc`), `HEADER_LEN_AFTER_HRPC_PART`, and `CURRENT_VERSION = 9`.

## Control Flow
There is no runtime flow. Client and server connection code reference these constants while parsing/writing headers and classifying special calls.

## State and Persistence Behavior
Only immutable constants exist. The wire protocol version affects compatibility of persisted clients/servers only through network negotiation.

## Dependencies and Integration Points
It integrates with `Client`, `Server`, `RetryCache`, SASL negotiation, ping handling, and connection context processing.

## Risks and Test Signals
Changing these constants breaks wire compatibility. Tests should cover connection header validation, special call ids, dummy client id skip in retry cache, and current-version negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcEngine.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcEngine.java

## Purpose
`RpcEngine` is the pluggable interface between the `RPC` facade and concrete serialization/transport implementations.

## Important APIs, Types, and Functions
It declares proxy creation by address or `ConnectionId`, proxy creation with auth fallback and alignment context, server construction, and `getProtocolMetaInfoProxy` for metadata queries reusing a connection id.

## Control Flow
`RPC` resolves an engine from configuration and delegates client/server construction. Implementations such as `ProtobufRpcEngine2` create dynamic proxies, clients, and servers.

## State and Persistence Behavior
The interface has no state. Implementations may maintain client caches or protocol registration state in memory.

## Dependencies and Integration Points
It depends on Hadoop `Configuration`, `RetryPolicy`, `Client.ConnectionId`, UGI, token secret managers, socket factories, and `AlignmentContext`.

## Risks and Test Signals
Risks include incomplete implementation of newer overloads, inconsistent auth/alignment handling, and metadata proxy misuse. Tests should exercise all overload paths for each engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcEngine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcException.java

## Purpose
`RpcException` is the base checked exception for errors during remote procedure call execution.

## Important APIs, Types, and Functions
It extends `IOException`, has package-private constructors for message and message-plus-cause, and provides the base for client/server RPC subclasses.

## Control Flow
Specific RPC code throws subclasses such as `RpcClientException`, `RpcServerException`, `RpcNoSuchMethodException`, and `RpcNoSuchProtocolException`.

## State and Persistence Behavior
Only inherited exception state exists. No persistence occurs.

## Dependencies and Integration Points
It integrates with response status/error-code mapping through subclasses.

## Risks and Test Signals
Risks are mainly diagnostic loss when generic exceptions are thrown instead of specific subclasses. Tests should assert remote response headers for server-specific subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcInvocationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcInvocationHandler.java

## Purpose
`RpcInvocationHandler` is the common dynamic-proxy handler contract for Hadoop RPC proxies.

## Important APIs, Types, and Functions
It extends `InvocationHandler` and `Closeable`, and requires `getConnectionId()` to expose the associated `Client.ConnectionId`.

## Control Flow
Dynamic proxies created by RPC engines route method calls through implementations. Utility code uses `Proxy.getInvocationHandler` and this interface for connection reuse and shutdown.

## State and Persistence Behavior
The interface has no state. Implementations store client, connection id, caches, and close state in memory.

## Dependencies and Integration Points
Implemented by protobuf engine invokers and `ProxyCombiner.CombinedProxyInvocationHandler`; consumed by `RPC.getConnectionIdForProxy`, `RPC.stopProxy`, and `RpcClientUtil`.

## Risks and Test Signals
Risks include proxy handlers not being closeable or returning wrong connection ids. Tests should verify proxy stop and metadata proxy connection reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcInvocationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcMultiplexer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcMultiplexer.java

## Purpose
`RpcMultiplexer` is the strategy interface used by `FairCallQueue` to choose which priority queue should be polled next.

## Important APIs, Types, and Functions
`getAndAdvanceCurrentIndex()` returns the current queue index and advances any internal schedule.

## Control Flow
`FairCallQueue.removeNextElement` calls this method after acquiring a semaphore permit, then falls back to scanning all queues if the chosen queue is empty.

## State and Persistence Behavior
The interface has no state. Implementations such as weighted round-robin maintain in-memory cursor/weight state.

## Dependencies and Integration Points
It integrates with priority-level queues and scheduler decisions in Hadoop IPC.

## Risks and Test Signals
Risks include returning out-of-range indexes or starving lower/higher priorities. Tests should plug deterministic multiplexers into `FairCallQueue` and verify dequeue distribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcMultiplexer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcNoSuchMethodException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcNoSuchMethodException.java

## Purpose
`RpcNoSuchMethodException` reports an RPC request for a method not present on the target protocol implementation.

## Important APIs, Types, and Functions
It extends `RpcServerException` and overrides status mapping to `RpcStatusProto.ERROR` and `RpcErrorCodeProto.ERROR_NO_SUCH_METHOD`.

## Control Flow
Protobuf invokers throw it when service descriptors cannot find the requested method name. The server response header carries its specialized error code.

## State and Persistence Behavior
Only exception message state exists. No persistence occurs.

## Dependencies and Integration Points
It integrates with `ProtobufRpcEngine2.Server.ProtoBufRpcInvoker` and RPC response header encoding.

## Risks and Test Signals
Risks include method name mismatches between generated client/server protos and incorrect mapping to generic server errors. Tests should call unknown methods and assert error code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcNoSuchMethodException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcNoSuchProtocolException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcNoSuchProtocolException.java

## Purpose
`RpcNoSuchProtocolException` reports an RPC request for a protocol not registered on the server.

## Important APIs, Types, and Functions
It extends `RpcServerException` and maps to `RpcStatusProto.ERROR` plus `RpcErrorCodeProto.ERROR_NO_SUCH_PROTOCOL`.

## Control Flow
`ProtobufRpcEngine2` throws it when no registered implementation exists for the requested declaring protocol name.

## State and Persistence Behavior
Only exception message state exists. No persistence occurs.

## Dependencies and Integration Points
It integrates with server protocol maps, protocol metadata, and RPC response header error-code mapping.

## Risks and Test Signals
Risks include annotation/protocol-name drift and clients treating it like retryable connection failure. Tests should cover unregistered protocol calls and response header codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcNoSuchProtocolException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcScheduler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcScheduler.java

## Purpose
`RpcScheduler` defines the priority, backoff, and response-time feedback interface used by Hadoop RPC servers to schedule calls.

## Important APIs, Types, and Functions
`getPriorityLevel(Schedulable)` returns queue priority. `shouldBackOff(Schedulable)` advises overload rejection/backoff. `addResponseTime(String, Schedulable, ProcessingDetails)` records timing feedback. A deprecated integer overload remains for old implementations. `stop()` shuts down scheduler resources.

## Control Flow
Server call admission asks priority/backoff methods. After a response, the server reports timing details. The default modern `addResponseTime` converts `ProcessingDetails` queue/processing times to the metrics default unit and delegates to the deprecated method for backward compatibility.

## State and Persistence Behavior
The interface has no state. Implementations may maintain in-memory decay counters, costs, or metrics.

## Dependencies and Integration Points
It depends on `Schedulable`, `ProcessingDetails`, and `RpcMetrics.DEFAULT_METRIC_TIME_UNIT`; used by call queues and scheduler implementations.

## Risks and Test Signals
Risks include old implementations throwing `UnsupportedOperationException` if they do not override the modern method, integer truncation, and inconsistent priority ranges. Tests should cover priority mapping, backoff decisions, timing feedback, and `stop`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcScheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcServerException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcServerException.java

## Purpose
`RpcServerException` is the base exception for server-side RPC failures that should map to explicit RPC response status and error code.

## Important APIs, Types, and Functions
It extends `RpcException`, has public constructors for message and cause, and defaults to `RpcStatusProto.ERROR` with `RpcErrorCodeProto.ERROR_RPC_SERVER`.

## Control Flow
Server-side code throws this or subclasses; response encoding consults the status/error-code methods.

## State and Persistence Behavior
Only exception message/cause state exists. No persistence occurs.

## Dependencies and Integration Points
It is the parent for version mismatch and no-such-method/protocol exceptions and integrates with RPC response header protos.

## Risks and Test Signals
Risks include returning generic server errors where specialized codes are expected. Tests should validate error-code mapping for base and subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcServerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcWritable.java

## Purpose
`RpcWritable` is the serialization abstraction used by Hadoop IPC for shaded protobuf messages, legacy unshaded protobuf messages, built-in Writables, and raw request/response buffers.

## Important APIs, Types, and Functions
`wrap(Object)` chooses `RpcWritable`, shaded `Message`, legacy protobuf, or `Writable` adapters. Old `Writable.readFields/write` are disabled. `WritableWrapper`, `ProtobufWrapper`, and `Buffer` implement optimized `writeTo` and `readFrom`. `Buffer.getValue` decodes a value from its current `ByteBuffer`.

## Control Flow
Serialization writes directly to `ResponseBuffer` with capacity preallocation. Shaded protobuf parsing reads a delimited message through `CodedInputStream` and advances the byte buffer by consumed bytes. `Buffer.readFrom` slices the remaining bytes and consumes them from the caller by changing the limit.

## State and Persistence Behavior
State is in-memory wrapper payload or byte buffer. No durable persistence is performed.

## Dependencies and Integration Points
It integrates with `Client`, `Server`, protobuf engines, SASL client access, `ResponseBuffer`, and tests in `TestRPC`/response buffer suites.

## Risks and Test Signals
Risks include assuming array-backed byte buffers, incorrect buffer position advancement, disabled writable methods surprising callers, and legacy protobuf detection order. Tests should cover shaded/legacy/writable round trips, raw buffer slicing, non-array buffers, and capacity preallocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Schedulable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Schedulable.java

## Purpose
`Schedulable` is the RPC call abstraction consumed by queues and schedulers. It exposes user identity, optional caller context, and priority level.

## Important APIs, Types, and Functions
`getUserGroupInformation()` returns the caller UGI. `getCallerContext()` defaults to throwing `UnsupportedOperationException` and is overridden by `Server.Call`. `getPriorityLevel()` returns the priority assigned by scheduling logic.

## Control Flow
Schedulers and `FairCallQueue` query these methods during call admission, priority selection, and identity attribution.

## State and Persistence Behavior
The interface has no state. Implementations represent live RPC calls and do not persist through this API.

## Dependencies and Integration Points
It depends on `UserGroupInformation` and `CallerContext`, and integrates with `RpcScheduler`, `IdentityProvider`, and `FairCallQueue`.

## Risks and Test Signals
Risks include callers assuming `getCallerContext` is always supported and priority values outside queue bounds. Tests should cover default exception behavior and valid priority mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Schedulable.java -->

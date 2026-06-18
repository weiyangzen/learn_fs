# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStateIdContext.java

## Purpose
`RouterStateIdContext` implements Hadoop IPC `AlignmentContext` for HDFS observer-read state propagation across a federated Router. It tracks last-seen state IDs per namespace from Namenode responses and attaches an eligible federated state map to client responses.

## Important APIs and Types
The class builds `coordinatedMethods` by reflecting over `ClientProtocol` methods annotated `@ReadOnly(isCoordinated=true)`. It maintains `ConcurrentHashMap<String, LongAccumulator> namespaceIdMap`, exposes `getNamespaceStateId`, `getNamespaces`, `getNamespaceIdMap`, `removeNamespaceStateId`, static `getRouterFederatedStateMap(ByteString)`, static `getClientStateIdFromCurrentCall`, `updateResponseState`, `receiveRequestState`, `isCoordinatedCall`, and package-visible `isNamespaceObserverReadEligible`.

## Control Flow
During RPC server construction, `RouterRpcServer` installs this alignment context into the IPC server and passes it into router RPC clients. Namenode response handling updates namespace accumulators elsewhere. On client response, `updateResponseState` calls `setResponseHeaderState`, which serializes namespace state IDs into `RouterFederatedStateProto` only for observer-read-eligible namespaces and only when the configured max-size limit is not exceeded. Request-side state from clients is intentionally ignored so clients cannot poison shared router state.

## State and Persistence
State is process-local and concurrent: one `LongAccumulator(Math::max, Long.MIN_VALUE)` per namespace. It is pruned by `RouterRpcServer.clearStaleNamespacesInRouterStateIdContext` when namespaces disappear from the resolver. No state is written to disk; state IDs travel in IPC protobuf headers.

## Dependencies and Integration Points
It depends on `ClientProtocol`, `@ReadOnly`, Hadoop IPC `Server.Call`, `RpcRequestHeaderProto`, `RpcResponseHeaderProto`, HDFS `RouterFederatedStateProto`, and observer-read config keys. It directly affects observer read consistency and `msync` behavior in async client protocol.

## Risks
The propagation size cap silently omits all federated state when the map is too large. Override logic uses XOR-like semantics: a namespace is eligible when the default differs from membership in the override set. Parsing invalid protobuf data throws a runtime exception. Shared accumulators must only be updated from trusted Namenode responses.

## Test Signals
Tests should cover coordinated method discovery, response header serialization under size cap, override/default observer eligibility combinations, stale namespace removal, parsing of federated state maps, and client state lookup from current IPC call.

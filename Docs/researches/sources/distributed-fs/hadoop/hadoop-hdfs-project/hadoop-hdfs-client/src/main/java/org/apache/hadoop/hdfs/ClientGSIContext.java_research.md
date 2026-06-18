# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ClientGSIContext.java

Purpose: client-side `AlignmentContext` implementation for global state ID propagation in RPC headers, including router federated state for Router-Based Federation.

Important APIs and functions: stores a `LongAccumulator` tracking max last-seen state ID and optional `routerFederatedState` `ByteString`. `receiveResponseState()` merges response state; `updateRequestState()` writes state into outbound request headers; static `getRouterFederatedStateMap()` parses `RouterFederatedStateProto`; `mergeRouterFederatedState()` keeps the max state ID per namespace.

Control flow: response handling prefers router federated state if present; otherwise it accumulates plain `stateId`. Request handling emits plain state ID only after the accumulator has moved from `Long.MIN_VALUE`, and emits federated state when present. Server-side methods are unsupported or no-op on the client.

State and persistence: state is in-memory per client context. `receiveResponseState()` and `updateRequestState()` are synchronized for the federated state field; the accumulator is thread-safe.

Dependencies and integration: integrates IPC alignment headers, generated HDFS protobufs, and protobuf `ByteString`.

Risks and test signals: invalid federated state bytes are silently treated as empty maps, which favors robustness but can hide corrupt state. Merge defaults missing namespace values to zero, so negative namespace state IDs would be normalized upward if ever introduced.

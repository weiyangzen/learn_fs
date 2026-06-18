# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederatedState.java

## Purpose

`TestRouterFederatedState.java` validates that router federated namespace state IDs can be serialized into an IPC request header through an `AlignmentContext` and parsed back as `RouterFederatedStateProto`. The source was read as a complete 104-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `AlignmentContext`, `ClientId`, `RPC.RpcKind`, `RpcHeaderProtos.RpcRequestHeaderProto`, `ProtoUtil.makeRpcRequestHeader`, and `HdfsProtos.RouterFederatedStateProto`. The local `AlignmentContextWithRouterState` implements `updateRequestState` by writing a `RouterFederatedStateProto` byte string into the request header.

## Control Flow

`testRpcRouterFederatedState` creates a client ID and an expected map of namespace state IDs, builds an RPC request header with the custom alignment context, extracts `header.getRouterFederatedState()`, parses it as `RouterFederatedStateProto`, and asserts that the resulting map equals the original map.

## State and Persistence Behavior

The only state is an in-memory `Map<String, Long>` held by the test alignment context and encoded into a protobuf field. There is no persistence beyond the request header byte string.

## Dependencies and Integration Points

This targets the IPC alignment extension point shared by HDFS clients, namenodes, and routers. It ensures `ProtoUtil.makeRpcRequestHeader` calls `AlignmentContext.updateRequestState` and that the router-specific protobuf field preserves namespace-state mappings.

## Risks and Edge Cases

The test only covers request-side propagation and does not exercise response state, threshold handling, coordinated-call detection, empty maps, duplicate keys, or malformed protobuf payloads. It still protects the key compatibility boundary between `AlignmentContext` and RPC header serialization.

## Test Signals

The primary signal is exact map equality after protobuf round trip. A regression would appear as an empty router state field, parse failure, or missing/changed namespace IDs.

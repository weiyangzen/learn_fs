# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtobufRpcEngine.proto

## Purpose
`ProtobufRpcEngine.proto` defines the request header for Hadoop's original protobuf RPC engine. It identifies the target method, declaring protocol, and client protocol version for each RPC request.

## Important APIs, types, and functions
The single message is `RequestHeaderProto` with required `methodName`, required `declaringClassProtocolName`, and required `clientProtocolVersion`. It is generated into `org.apache.hadoop.ipc.protobuf.ProtobufRpcEngineProtos`.

## Control flow
For every protobuf-engine RPC, the client sends this header before the serialized protobuf request body. The server uses method name and declaring protocol to resolve the Java method and protocol implementation, while client protocol version participates in compatibility checks. Response headers are handled by `RpcHeader.proto`.

## State and persistence
The header is per RPC call. Required fields make malformed or incomplete call headers fail protobuf initialization/parsing.

## Dependencies and integration points
It is consumed by `ProtobufRpcEngine`, `ProtobufRpcEngine2` compatibility paths, Hadoop IPC server dispatch, and generated Java under `src/main/proto2-generated`.

## Risks and test signals
Risks include method-name drift, wrong declaring protocol for meta-protocol calls, required-field incompatibility, and generated-code skew with the proto. Test signals include RPC engine unit tests, protocol metadata calls, mixed client/server protocol versions, and generated Java regeneration diffs.

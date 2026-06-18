# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtobufRpcEngine2.proto

## Purpose
`ProtobufRpcEngine2.proto` defines the same per-call request header shape for Hadoop's newer protobuf RPC engine namespace. It supports the `ProtobufRpcEngine2` implementation while preserving the established method/protocol/version contract.

## Important APIs, types, and functions
The single `RequestHeaderProto` message has required fields `methodName`, `declaringClassProtocolName`, and `clientProtocolVersion`. It generates `org.apache.hadoop.ipc.protobuf.ProtobufRpcEngine2Protos`.

## Control flow
Clients using `ProtobufRpcEngine2` prepend this header to each protobuf request body. Servers dispatch using the method name and declaring protocol and validate protocol version compatibility.

## State and persistence
The message is transient per call. Required fields prevent partially initialized headers from being built by generated Java code.

## Dependencies and integration points
It integrates with `ProtobufRpcEngine2`, Hadoop IPC request deserialization, protocol translators, and RPC client utility code that selects the newer engine.

## Risks and test signals
Risks include divergence from the original engine header, mismatch between generated and handwritten RPC code, and mixed-engine compatibility issues. Test signals include engine2 RPC tests, backward compatibility tests with original engine clients where supported, meta-protocol calls, and generated-source checks.

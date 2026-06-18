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

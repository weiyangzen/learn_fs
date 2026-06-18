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

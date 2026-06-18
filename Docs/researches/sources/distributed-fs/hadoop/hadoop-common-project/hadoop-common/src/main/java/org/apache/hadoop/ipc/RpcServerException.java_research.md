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

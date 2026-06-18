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

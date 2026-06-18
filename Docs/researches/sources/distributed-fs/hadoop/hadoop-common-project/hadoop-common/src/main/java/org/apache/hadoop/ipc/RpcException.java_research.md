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

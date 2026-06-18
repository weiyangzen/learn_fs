# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingClientConnection.java

## Purpose
`GrpcMessagingClientConnection` specializes `GrpcMessagingConnection` for client-owned streams and closes the underlying gRPC channel when the logical connection closes.

## Important APIs, Types, and Functions
It defines a constructor and overrides `close()`. It stores a `GrpcChannel` and passes owner `CLIENT`, the channel key string, context, executor, and request timeout to the base class.

## Control Flow, State, and Persistence
The connection itself has no persistence. `close()` chains from `super.close()`, then attempts `mChannel.shutdown()` in a `finally` path and completes its result future with `null` even if shutdown logs a warning.

## Dependencies and Integration Points
It depends on the base connection state machine and Alluxio gRPC channel abstraction. It is created by `GrpcMessagingClient.connect()`.

## Risks and Test Signals
Risks include swallowing channel shutdown failures, completing close successfully even after base close errors, and requiring `setTargetObserver()` before use. Signals are pending request failure on close, stream completion, and channel shutdown invocation.

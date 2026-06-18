# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServerConnection.java

## Purpose
`GrpcMessagingServerConnection` specializes `GrpcMessagingConnection` for server-owned streams.

## Important APIs, Types, and Functions
It defines a constructor that passes owner `SERVER`, the transport id, context, executor, and request timeout to the base class.

## Control Flow, State, and Persistence
The class adds no additional state or persistence behavior. Server-specific completion behavior is handled by the base class through the `ConnectionOwner.SERVER` value.

## Dependencies and Integration Points
It depends on `GrpcMessagingConnection` and is instantiated by `GrpcMessagingServiceClientHandler.connect()`.

## Risks and Test Signals
Risks include relying entirely on base-class behavior and needing `setTargetObserver()` before use. Signals are server stream completion propagating to the client observer and server-side request/response handling.

# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingClient.java

## Purpose
`GrpcMessagingClient` creates outbound bidirectional messaging connections to remote embedded-journal transport servers.

## Important APIs, Types, and Functions
The main methods are the constructor, `connect(InetSocketAddress)`, and `close()`. It uses `GrpcChannelBuilder`, `GrpcServerAddress`, `MessagingServiceGrpc.MessagingServiceStub`, `GrpcMessagingClientConnection`, `GrpcMessagingContext.currentContextOrThrow()`, `UserState`, and request timeout configuration.

## Control Flow, State, and Persistence
`connect()` must be called from a `GrpcMessagingContext` thread. It builds the gRPC channel asynchronously on the transport executor, creates a stub, constructs a client connection, binds the connection as the response observer for `stub.connect()`, then completes the returned future back on the originating context. `close()` has no owned connection list and returns an already-completed future.

## Dependencies and Integration Points
It is created by `GrpcMessagingTransport.client()`, shares the transport executor, and authenticates channels with the configured user subject. It integrates with `GrpcMessagingConnection` for message serialization and lifecycle.

## Risks and Test Signals
Risks include calling from outside a messaging context, leaking channels if callers do not close returned connections, and `RuntimeException` wrapping of build errors. Signals are successful connection futures on the context thread, subject propagation, failure completion for channel build errors, and channel shutdown through `GrpcMessagingClientConnection.close()`.

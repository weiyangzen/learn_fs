# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingServer.java

## Purpose
`GrpcMessagingServer` opens a gRPC server endpoint for embedded-journal messaging connections.

## Important APIs, Types, and Functions
Key methods are the constructor, `listen(InetSocketAddress, Consumer<GrpcMessagingConnection>)`, and `close()`. It uses `GrpcServerBuilder`, `GrpcService`, `GrpcMessagingServiceClientHandler`, `ClientContextServerInjector`, `GrpcMessagingProxy`, and max inbound message size/request timeout configuration.

## Control Flow, State, and Persistence
`listen()` is synchronized and reuses an existing non-exceptional listen future. It captures the current messaging context, resolves proxy bind address if configured, builds a gRPC server with the messaging service and client-context interceptor, starts it asynchronously on the transport executor, and stores the server reference. `close()` asynchronously shuts down the gRPC server and clears the reference.

## Dependencies and Integration Points
It is created by `GrpcMessagingTransport.server()` and provides the server side consumed by `GrpcMessagingClient.connect()`. It integrates with security context injection, Alluxio gRPC server configuration, and the caller's connection listener.

## Risks and Test Signals
Risks include listen calls outside a messaging context, reuse of a failed listen future semantics, asynchronous close using the common pool instead of the transport executor, and proxy misconfiguration. Signals are successful bind/start, max message size enforcement, listener invocation for new streams, proxy binding, and server shutdown releasing the port.

# sources/cloud-native/moby/daemon/server/router/grpc/grpc_routes.go

## Purpose
`grpc_routes.go` implements the HTTP upgrade path that serves the gRPC server over a hijacked h2c connection.

## Important APIs, Types, And Functions
`serveGRPC` requires `http.Hijacker`, checks `Upgrade: h2c`, hijacks the connection, writes a `101 Switching Protocols` response, and calls `http2.Server.ServeConn` with the gRPC server as handler.

## Control Flow
Requests without upgrade or with any protocol other than h2c fail before hijack. After hijack, the function writes the upgrade response directly to the raw connection and transfers control to the HTTP/2 server.

## State And Persistence
No persistent state is written. The connection is removed from normal HTTP server management after hijack.

## Dependencies And Integration Points
Depends on `net/http`, `http2`, and the `grpcRouter` server fields. It is the implementation for POST `/grpc`.

## Risks
After hijack, normal HTTP error handling no longer applies. The code manually writes response bytes and has a TODO about serving a connection after it has already been written to.

## Test Signals
Integration tests for deprecated `/grpc` clients are the primary signal.

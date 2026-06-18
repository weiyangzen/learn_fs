<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/httphandler.go -->
# sources/cloud-native/moby/daemon/command/httphandler.go

## Purpose
Multiplexes Docker HTTP API traffic and BuildKit/gRPC traffic on the same HTTP server and configures daemon gRPC tracing/error interceptors.

## Important APIs, Types, And Functions
`httpHandler`, `newHTTPHandler`, `ServeHTTP`, `newGRPCServer`, and `unaryInterceptor`.

## Control Flow
`ServeHTTP` routes HTTP/2 requests with `application/grpc` content to the gRPC server and all other requests to the API handler. `newGRPCServer` installs OTEL stats and BuildKit error interceptors. The unary interceptor skips tracing export calls to avoid recursive traces and logs other gRPC errors.

## State And Persistence Behavior
Keeps references to context, gRPC server, and API handler. No disk persistence. In debug logging, stack traces are written to stderr.

## Dependencies And Integration Points
Integrates BuildKit tracing/error helpers, daemon OTEL utilities, containerd defaults for message sizes, and the Docker API server.

## Risks And Test Signals
Risks include protocol/content-type misclassification, trace-export recursion, and stderr stack output volume under debug. Test signals are mostly integration-level API and BuildKit gRPC behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/httphandler.go -->

# sources/cloud-native/moby/daemon/server/router/grpc/grpc.go

## Purpose
`grpc.go` builds the deprecated `/grpc` router, wrapping a gRPC server behind an h2c HTTP upgrade endpoint with tracing and buildkit-compatible error handling.

## Important APIs, Types, And Functions
`grpcRouter` stores routes, a `grpc.Server`, and an `http2.Server`. `NewRouter` configures tracing stats handlers, unary/stream error interceptors, send/receive limits, registers supplied backends, and registers `/grpc`. `unaryInterceptor` logs failed unary calls except trace export calls.

## Control Flow
Router construction creates an OpenTelemetry tracer provider, configures gRPC server options, lets each backend register services, then exposes one POST route. Unary calls run through a custom interceptor and BuildKit gRPC error interceptor chain.

## State And Persistence
The gRPC server and h2 server are in-memory service dispatch state. No durable state is managed here.

## Dependencies And Integration Points
Integrates containerd defaults, BuildKit `grpcerrors`, OpenTelemetry gRPC instrumentation, daemon `otelutil`, `http2`, and the shared router package.

## Risks
The endpoint is deprecated; new clients should use direct HTTP/2/h2c. Tracing export is intentionally excluded from tracing to avoid recursive trace loops. Debug stack formatting to stderr only happens at debug log level.

## Test Signals
No direct tests; behavior depends on gRPC integration tests and any BuildKit/session services registered through this router.

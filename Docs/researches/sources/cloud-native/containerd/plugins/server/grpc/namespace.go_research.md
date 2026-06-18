# sources/cloud-native/containerd/plugins/server/grpc/namespace.go

## Purpose
Provides gRPC interceptors that preserve namespace context from incoming metadata into outgoing context values.

## Important APIs, Types, And Functions
`unaryNamespaceInterceptor` wraps unary calls. `streamNamespaceInterceptor` wraps stream calls with `wrappedSSWithContext`. `wrappedSSWithContext.Context` returns the replacement context.

## Control Flow
Each interceptor checks `namespaces.Namespace(ctx)`, and when present, re-applies it with `namespaces.WithNamespace` before invoking the handler.

## State And Persistence
No persistence. It only modifies request context.

## Dependencies And Integration Points
Used by gRPC server construction for all registered services. Depends on containerd namespace metadata helpers and gRPC interceptors.

## Risks
If namespace metadata parsing changes, all services can receive incorrect namespace context. Streams require wrapper correctness to avoid losing other stream behavior.

## Test Signals
No direct tests in this subset.

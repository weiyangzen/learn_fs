## sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/namespaces.go

Purpose: gRPC interceptors that preserve containerd namespace metadata on outgoing contexts.

Important APIs/types/functions: `unaryNamespaceInterceptor`, `streamNamespaceInterceptor`, and `wrappedSSWithContext`.

Control flow: for unary and stream RPCs, read incoming namespace using `namespaces.Namespace(ctx)`. If present, wrap the context with `namespaces.WithNamespace`; stream calls wrap `grpc.ServerStream` so `Context()` returns the updated context.

State and persistence: no durable state; modifies request context only.

Dependencies and integration: copied from containerd server namespace handling and used by the daemon's gRPC server options.

Risks and test signals: no direct tests in this subset; correctness depends on containerd namespace metadata format and interceptor ordering.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/grpc.go -->
# sources/cloud-native/containerd/client/grpc.go

Purpose: namespace-injecting gRPC client interceptors used when a client has a default namespace.

Important APIs/types/functions: `namespaceInterceptor`, its `unary` and `stream` methods, and `newNSInterceptors`.

Control flow: each interceptor checks whether the context already has a namespace; if absent, it adds the configured default namespace before invoking the unary or stream RPC.

State/persistence: no durable state; the namespace value travels in context metadata through downstream namespace machinery.

Dependencies/integration: containerd namespaces package and gRPC interceptor APIs. `New` installs these interceptors when `WithDefaultNamespace` is set.

Risks: callers using `WithDialOpts` can replace default dial options and skip these interceptors unless they add equivalents. Existing namespace in context always wins over default.

Test signals: unary and stream namespace injection, preservation of explicit namespace, interaction with custom dial options, and service calls under default namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/grpc.go -->

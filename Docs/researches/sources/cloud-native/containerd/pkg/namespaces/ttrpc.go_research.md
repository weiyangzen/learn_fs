# sources/cloud-native/containerd/pkg/namespaces/ttrpc.go

Purpose: ttrpc metadata carrier for containerd namespace propagation.

Important APIs/types/functions: `TTRPCHeader = "containerd-namespace"`; `withTTRPCNamespaceHeader(ctx, namespace)` clones existing metadata or creates a new map, sets the namespace, and returns a context with metadata. `fromTTRPCHeader(ctx)` extracts the first namespace value.

Control flow: metadata is cloned before mutation to avoid aliasing callers' maps. Lookup returns false on absent metadata or absent header values.

State/persistence: context metadata only.

Dependencies/integration: used by `WithNamespace` and `Namespace`. Depends on `github.com/containerd/ttrpc`.

Risks: only the first value is used when multiple values exist. Header key must remain aligned with gRPC and service expectations.

Test signals: `ttrpc_test.go` verifies metadata clone independence and namespace header round trip.

# sources/cloud-native/containerd/pkg/namespaces/grpc.go

Purpose: gRPC metadata carrier for containerd namespace propagation.

Important APIs/types/functions: `GRPCHeader = "containerd-namespace"`; `withGRPCNamespaceHeader(ctx, namespace)` creates metadata pair and joins it ahead of existing outgoing metadata; `fromGRPCHeader(ctx)` reads the first namespace value from incoming metadata.

Control flow: outgoing writes preserve existing metadata while placing the latest namespace first. Incoming reads do not inspect outgoing metadata and return false when metadata or values are absent.

State/persistence: context metadata only.

Dependencies/integration: used by `WithNamespace` and `Namespace`. Depends on `google.golang.org/grpc/metadata`.

Risks: multiple namespace values can exist; readers take index 0. Outgoing context is not checked on reads, so client-side contexts without incoming metadata rely on the direct context value.

Test signals: no direct gRPC-specific test in this subset, but namespace context tests plus RPC integration should verify header propagation between clients and servers.

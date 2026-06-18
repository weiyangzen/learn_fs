# sources/cloud-native/containerd/pkg/namespaces/ttrpc_test.go

Purpose: tests ttrpc metadata behavior used by namespace propagation.

Important APIs/types/functions: `TestCopyTTRPCMetadata` confirms `ttrpc.MD.Clone` deep-copies value slices by mutating the original after clone. `TestTTRPCNamespaceHeader` verifies `withTTRPCNamespaceHeader` and `fromTTRPCHeader` round-trip a namespace string.

Control flow: create metadata/context, mutate or extract values, compare with `reflect.DeepEqual` or direct string checks.

State/persistence: context metadata only.

Dependencies/integration: uses `github.com/containerd/ttrpc`.

Risks: tests do not cover multiple namespace header values or interaction with direct context values. The clone test partly tests upstream ttrpc behavior, not only this package.

Test signals: protects against metadata aliasing bugs and ensures ttrpc clients receive the same namespace header key as gRPC clients.

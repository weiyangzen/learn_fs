# sources/cloud-native/containerd/core/metrics/cgroups/common/type.go

Purpose: defines the shared interface used by cgroup metrics collectors to get task identity, namespace, and encoded stats.

Important APIs and types: `Statable` requires `ID() string`, `Namespace() string`, and `Stats(context.Context) (*types.Any, error)`.

Control flow: no runtime logic; v1 and v2 collectors accept `common.Statable` entries and call `Stats` under a namespaced timeout context during Prometheus collection.

State and persistence: none.

Dependencies and integration: depends on context and containerd protobuf `types.Any`. It bridges runtime tasks and metrics collectors without importing runtime task concrete types into descriptor files.

Risks: collectors assume returned `Any` can be unmarshaled into the selected cgroup version metrics type. Mismatched cgroup mode and stats payload type cause logged collection errors rather than returned errors.

Test signals: `metrics_test.go` defines `mockStatT` implementing this interface for concurrency regression coverage.

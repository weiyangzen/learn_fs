# sources/control-plane/rook/pkg/operator/ceph/object/bucket/controller_test.go

## Purpose
`controller_test.go` validates the high-level bucket controller reconcile behavior around CephCluster presence and provisioner startup.

## Important APIs, Types, and Functions
The suite tests `ReconcileBucket.Reconcile()` through two subtests. It builds fake controller-runtime clients, fake client-go clients, a `clusterd.Context`, `OperatorConfig`, `CephCluster`, monitor Secret, and lib-bucket-provisioner object types. It uses a dummy `rest.Config{}` because lib-bucket-provisioner expects a kubeconfig.

## Control Flow, State, and Persistence
The first subtest reconciles without a CephCluster and expects no error and no requeue. The second creates a CephCluster and monitor Secret, sets a fake kubeconfig, starts reconcile with a cancelable context, waits briefly for the bucket manager goroutine to start, and cancels the context. Persistent fake state includes the monitor Secret needed by `LoadClusterInfo`.

## Dependencies and Integration Points
The tests integrate controller-runtime fake clients, the Rook scheme, Kubernetes Secrets, lib-bucket-provisioner API types, and Rook cluster-info loading. Comments document why deeper mocking of lib-bucket-provisioner is difficult due to unexported internals.

## Risks
The "success" test mostly verifies no immediate error; it does not prove the bucket controller can list/watch resources against a real API server. It sleeps for two seconds, which can add test latency and still be timing-sensitive. The test does not cover environment-based disabling, cleanup policy skip, missing monitor Secret requeue semantics, duplicate CephCluster predicate behavior, or goroutine error handling.

## Test Signals
Useful current signals are that reconcile is inert when no cluster exists and that the startup path can be invoked with fake cluster credentials. Additional signals should assert no duplicate controllers across multiple reconciles and verify `ROOK_OBC_WATCH_OPERATOR_NAMESPACE` reload behavior through predicate tests.

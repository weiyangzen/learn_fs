# sources/control-plane/rook/pkg/operator/ceph/pool/radosnamespace/controller_test.go

Purpose: unit/integration-style test coverage for the RADOS namespace reconciler using fake controller-runtime clients, fake Kubernetes clients, and mock Ceph command execution.

Important APIs/types/functions: `TestCephBlockPoolRadosNamespaceController`, `Test_buildClusterID`, and `TestGetRadosNamespaceName`. The main test constructs `CephBlockPoolRadosNamespace`, `CephCluster`, `CephBlockPool`, secrets, fake CSI config, and a `ReconcileCephBlockPoolRadosNamespace` directly instead of going through manager setup.

Control flow: the primary test mutates shared test objects across subtests to move through controller states. It first verifies reconcile requeues when no cluster or an unready cluster is present. It then injects monitor secrets and a ready pool to validate successful create, Ready status, and CSI config presence. Further subtests toggle external mode and mirroring specs, with mock command handlers matching `namespace create`, `mirror pool info`, `mirror pool enable`, `mirror pool disable`, `mirror pool status`, and `versions`.

State and persistence behavior: fake Kubernetes object trackers persist CR status changes and config maps across individual test branches. The test also creates a Rook clientset namespace resource and a Kubernetes secret so `LoadClusterInfo` can assemble cluster info. Environment variables such as `POD_NAMESPACE` and `ROOK_LOG_LEVEL` influence CSI config and logging setup.

Dependencies/integration: uses Rook fake clientsets, controller-runtime fake client, Ceph API scheme registration, `csi.CreateCsiConfigMap`, `k8sutil.NewOwnerInfoWithOwnerRef`, and `exectest.MockExecutor`.

Risks: many subtests reuse and mutate objects like `cephCluster`, `cephBlockPool`, and `cephBlockPoolRadosNamespace`; this can hide ordering dependencies. Some assertions check only result/error/status and not all created/updated resources. Deletion paths, finalizer removal, duplicate CR field index behavior, cleanup jobs, and long-running mirror goroutine cancellation are not strongly exercised.

Test signals: positive signals include coverage for cluster readiness gates, block pool readiness, external mode, successful CSI profile update, mirror-mode compatibility with block pool mirroring, remote namespace argument placement, mirroring disable with empty image list, deterministic cluster ID generation, and implicit namespace name mapping.

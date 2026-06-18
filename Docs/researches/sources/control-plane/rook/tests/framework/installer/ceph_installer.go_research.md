# sources/control-plane/rook/tests/framework/installer/ceph_installer.go

Purpose: `CephInstaller` is the main integration-test orchestrator for installing, validating, and uninstalling Rook/Ceph clusters through kubectl or Helm.

Important APIs/types/functions: Ceph image/version constants; `CephInstaller` struct; `ReturnCephVersion`; install methods `CreateCephOperator`, `CreateCephCluster`, `CreateRookExternalCluster`, `InstallRook`; wait/validation helpers `waitForCluster`, `WaitForToolbox`, `checkCephHealthStatus`; cleanup methods `UninstallRookFromMultipleNS`, `waitForResourceDeletion`, `removeClusterFinalizers`, `waitForCleanupJobs`; constructor `NewCephInstaller`.

Control flow: non-Helm install creates CRDs, optional hostname mutations, namespaces/RBAC, volume replication CRDs, CSI operator, operator manifest, optional NFS CSI driver, cluster config maps, CephCluster CR with retries, and toolbox. Helm install delegates to Helm-specific methods. `InstallRook` pulls required images, installs the operator, installs the cluster, waits for pods/toolbox/status, and validates Helm defaults when needed. Uninstall collects logs/restart counts, skips cleanup on test failure, optionally adds cleanup policy and checks health, deletes cluster resources through Helm or kubectl, waits for finalizers and cleanup jobs, deletes common/operator/CSI/CRD resources, removes namespaces, verifies host data dir cleanup, and restores hostname labels.

State and persistence behavior: mutates substantial external state: Kubernetes namespaces, CRDs, RBAC, config maps, secrets, CephCluster and dependent CRs, pods/jobs, host data directories, node labels, Helm releases, and global Ceph client toolbox routing (`client.RunAllCephCommandsInToolboxPod`).

Dependencies and integration points: depends on Kubernetes typed clients, Rook clientsets, Ceph client helpers, manifest generators, Helm helper, test environment variables, remote URLs for volume replication CRDs, and Kubernetes wait primitives.

Risks: global and environmental side effects are broad. Cleanup is intentionally skipped on failed tests, leaving clusters for investigation. Forced finalizer removal after repeated waits can mask operator teardown bugs. External URL dependencies and image pulls add CI flake. `InstallCSIOperator` returns `err` after a readiness failure where `err` may be nil, weakening error reporting.

Test signals: operator pod readiness, CSI operator readiness, mon/mgr/osd pod counts, toolbox command success, Ceph status, cleanup job completion, namespace deletion, host path verification, and collected logs/events on failure.

# sources/control-plane/rook/tests/integration/ceph_helm_test.go

Suite-level integration coverage for installing Rook/Ceph via Helm and validating basic block, file, and object functionality on that Helm-managed cluster.

`HelmSuite` stores helper, installer, settings, and Kubernetes helper. `SetupSuite` configures namespace `helm-ns`, Helm install, one mon, raw-device OSDs, discovery, hostname changes, encrypted connections, Squid Ceph, and CSI operator. Tests call shared install/ingress checks, block-lite, file-lite, and object-lite helpers. `AfterTest` collects operator logs; teardown uninstalls Rook.

State includes Helm releases, namespace resources, Rook/Ceph cluster resources, block pools/PVCs, CephFS resources/snapshots/clones, and lite object store resources. Dependencies are Helm-capable `CephInstaller`, shared deploy/block/file/object helpers, `clients.CreateTestClient`, and testify suite lifecycle.

Risks: shared helper fixed names can affect later test methods after failures; Helm chart behavior can differ from manifest installs; all storage validations share one cluster so setup instability cascades. Signals are pod counts, dashboard ingress, block/file snapshot and clone checks, object-store readiness/deletion, operator logs, and final uninstall.

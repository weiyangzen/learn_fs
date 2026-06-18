# sources/control-plane/rook/tests/framework/installer/ceph_helm_installer.go

Purpose: this file implements Helm-based Rook operator, Ceph cluster, and Ceph CSI driver installation flows for integration tests.

Important APIs/types/functions: chart constants for `rook-ceph`, `rook-ceph-cluster`, and Ceph CSI drivers; default test resource names; `CreateRookOperatorViaHelm`, `UpgradeRookOperatorViaHelm`, `CreateRookCephClusterViaHelm`, `UpgradeRookCephClusterViaHelm`; `InstallCephCsiDriversViaHelm`; Helm cleanup/validation helpers; configuration builders for block, filesystem, and object store chart values.

Control flow: operator installation builds values for discovery, image tag, monitoring, history, and host network, creates the operator namespace, then installs local or versioned charts based on `RookVersion`. Cluster installation initializes `DataDirHostPath`, unmarshals generated CephCluster YAML to feed `cephClusterSpec`, adds toolbox/monitoring/ingress config, appends default storage CR values, installs/upgrades the chart, and optionally installs Ceph CSI drivers for local Helm tests. CSI driver installation creates snapshot CRDs/controller, waits for readiness, then installs a repo chart with RBD/CephFS and optional NFS drivers.

State and persistence behavior: persistent state includes Helm releases, namespaces, CRDs, Ceph custom resources, storage classes, Prometheus rules, CSI operator resources, and generated temporary Helm values files in the helper.

Dependencies and integration points: depends on `CephInstaller`, `HelmHelper`, `K8sHelper`, generated manifests, YAML marshal/unmarshal, snapshot helpers, and external Helm repositories.

Risks: chart value maps are loosely typed, so YAML schema drift may fail late. External repo/chart versions and Prometheus bundle URLs create network/version risk. Cleanup asserts not-found behavior but does not handle all asynchronous finalizers. Default Helm storage CR cleanup can interfere with tests if retention flags are wrong.

Test signals: successful Helm release install/upgrade, operator and cluster readiness, three expected storage classes, two RGW pods for the default object store, CSI driver deployment, and successful cleanup of default CRs.

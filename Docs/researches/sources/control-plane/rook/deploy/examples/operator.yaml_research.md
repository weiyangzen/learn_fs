# sources/control-plane/rook/deploy/examples/operator.yaml

Purpose: deploys the standard Rook Ceph operator and CSI driver configuration for Kubernetes.

Important APIs/types/functions: `ConfigMap/rook-ceph-operator-config` with `ROOK_*` settings, CSI image set ConfigMap, `OperatorConfig/ceph-csi-operator-config`, RBD and CephFS `Driver` CRs, and `Deployment/rook-ceph-operator` using image `docker.io/rook/ceph:master`.

Control flow: Kubernetes starts the operator deployment under service account `rook-ceph-system`; the operator reads config values, reconciles Ceph CRDs, and coordinates CSI operator/driver resources.

State and persistence: configuration persists in ConfigMaps and CSI CRs; operator runtime state is stateless apart from Kubernetes leader/reconcile state and managed Ceph resources.

Dependencies/integration: requires CRDs, common RBAC/service accounts, CSI operator CRDs, and a namespace named `rook-ceph`.

Risks: mutable `master` image tag, many commented config toggles, disabled operator metrics bind address by default, and hard-coded namespace expectations.

Test signals: operator pod ready, no config parse errors, CSI driver resources created, and creating a `CephCluster` triggers reconciliation.

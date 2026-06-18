
# sources/control-plane/rook/deploy/examples/cluster-external-management.yaml

Purpose: defines a minimal external-mode `CephCluster` for a cluster namespace where an already-running Rook operator manages an external Ceph cluster.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephCluster`, metadata `rook-ceph-external`, `spec.external.enable: true`, `dataDirHostPath`, and `cephVersion.image: quay.io/ceph/ceph:v20.2.1`.

Control flow: after `common-external.yaml` creates namespace/RBAC, applying this CR tells the operator to reconcile an external cluster rather than create mons/OSDs. The Ceph image is present so other Rook CRs such as RGW, MDS, or NFS can run helper daemons compatible with the external cluster.

State and persistence: the CR persists external cluster desired state and status; actual Ceph data lives outside this Kubernetes cluster or outside Rook management.

Dependencies/integration: depends on common RBAC for the external namespace, external cluster connection secrets/config expected by Rook external mode, and matching Ceph version/image compatibility.

Risks: the external cluster version must match the configured image. Missing external credentials leaves the CR unreconciled. Reusing `dataDirHostPath` across multiple clusters can collide with local state.

Test signals: apply after external common resources and imported connection secrets; verify CephCluster status, operator logs, and successful creation of dependent external-mode CRs such as object stores or filesystems.

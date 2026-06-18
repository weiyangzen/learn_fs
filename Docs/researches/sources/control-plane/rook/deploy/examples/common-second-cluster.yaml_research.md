
# sources/control-plane/rook/deploy/examples/common-second-cluster.yaml

Purpose: provides RBAC and service accounts needed for a second Rook Ceph cluster namespace, `rook-ceph-secondary`, managed by an operator in `rook-ceph`.

Important APIs/types/functions: Kubernetes `Namespace`, RoleBindings to `rook-ceph-cluster-mgmt`, `rook-ceph-cmd-reporter`, and `rook-ceph-mgr-system`; service accounts for cmd reporter, default, mgr, OSD, purge OSD, and RGW; roles for cmd reporter, OSD, purge OSD, and mgr; ClusterRole/ClusterRoleBinding for OSD node listing; and ClusterRoleBinding for mgr cluster access.

Control flow: base `common.yaml` creates shared ClusterRoles. This file creates namespace-local identities and binds them so the operator can reconcile a second CephCluster and its daemons in the secondary namespace.

State and persistence: all objects are persistent Kubernetes namespace/RBAC/identity state. They authorize creation, deletion, purging, and manager-module operations for a second cluster, but do not store Ceph data directly.

Dependencies/integration: depends on base ClusterRoles from `common.yaml`, operator watch scope, and any secondary CephCluster manifest applied later.

Risks: comments mention templating, but the checked-in manifest is hardcoded to `rook-ceph-secondary`. RBAC is broad, including deployment deletion, PVC deletion, and Ceph CR patch/update. Static ClusterRoleBinding names can collide if copied without renaming.

Test signals: run auth checks for operator, mgr, OSD, and purge service accounts; apply a secondary cluster; verify resources stay isolated to `rook-ceph-secondary` except expected cluster-wide mgr/OSD node access.

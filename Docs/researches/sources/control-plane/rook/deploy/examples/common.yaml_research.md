
# sources/control-plane/rook/deploy/examples/common.yaml

Purpose: creates the foundational namespace, service accounts, ClusterRoles, Roles, and bindings required before deploying the Rook Ceph operator and cluster examples in the `rook-ceph` namespace.

Important APIs/types/functions: Kubernetes `Namespace`, `ClusterRole`, `ClusterRoleBinding`, `Role`, `RoleBinding`, and `ServiceAccount`. Major roles include `objectstorage-provisioner-role`, `rook-ceph-cluster-mgmt`, `rook-ceph-global`, `rook-ceph-mgr-cluster`, `rook-ceph-mgr-system`, `rook-ceph-object-bucket`, `rook-ceph-osd`, `rook-ceph-system`, `rook-ceph-cmd-reporter`, `rook-ceph-mgr`, `rook-ceph-osd`, and `rook-ceph-purge-osd`.

Control flow: users apply this before `operator.yaml` and cluster manifests. It grants the operator global watch/update/status/finalizer access for Rook CRDs, namespace management rights for workloads/secrets/services/configmaps, object bucket provisioning permissions, mgr module permissions, OSD topology permissions, purge job permissions, CSI operator resource permissions, and COSI provisioning permissions.

State and persistence: the file creates durable authorization and identity state. It does not persist Ceph data, but it gates every later reconciliation path and allows controllers to create persistent secrets, CRs, PVCs, PVs, services, deployments, jobs, and events.

Dependencies/integration: must stay synchronized with Rook CRDs, manager/operator code, CSI and COSI APIs, ObjectBucket APIs, OpenShift machine/disruption APIs, Multus network attachment definitions, and all example cluster manifests.

Risks: RBAC is intentionally broad and cluster-scoped. Missing new CRD resources breaks reconciliation after upgrades, while over-broad permissions increase service-account compromise impact. Static names assume one primary Rook deployment per cluster/namespace.

Test signals: compare role resource lists with CRDs and controllers, run `kubectl auth can-i` matrices for operator/mgr/OSD/purge/COSI accounts, and perform an end-to-end apply of common, operator, and a sample cluster.

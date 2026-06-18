
# sources/control-plane/rook/deploy/examples/common-external.yaml

Purpose: creates namespace-local prerequisites for managing an external Ceph cluster in `rook-ceph-external` while an operator runs in `rook-ceph`.

Important APIs/types/functions: Kubernetes `Namespace`, `RoleBinding` to `ClusterRole/rook-ceph-cluster-mgmt`, `RoleBinding` to `Role/rook-ceph-cmd-reporter`, service accounts `rook-ceph-cmd-reporter` and `rook-ceph-default`, and a namespaced `Role` allowing pod/configmap get/list/watch/create/update/delete.

Control flow: after the base operator/common resources exist, this manifest adds the external namespace and grants the operator service account permission to manage cluster-scoped workloads in that namespace. It also creates the command reporter identity used by Rook helper jobs.

State and persistence: namespace, RBAC, and service accounts persist as Kubernetes control-plane state. They do not store Ceph data but authorize external-mode reconciliation.

Dependencies/integration: depends on `common.yaml` having created `rook-ceph-cluster-mgmt` and on the operator watching `rook-ceph-external`. It pairs with `cluster-external.yaml` or `cluster-external-management.yaml`.

Risks: if the operator is configured current-namespace-only, it will not watch the external namespace. Subject namespace/name mismatches leave reconciliation unauthorized. The sample assumes `rook-ceph-external` unless edited.

Test signals: apply after base common/operator resources, run `kubectl auth can-i` as the operator service account in the external namespace, and verify external CephCluster reconciliation starts.

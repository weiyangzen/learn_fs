<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/common-external.yaml -->
# sources/control-plane/rook/deploy/examples/external/common-external.yaml

Purpose: common namespace, service accounts, roles, and role bindings required for external Ceph cluster mode.
Important APIs/types/functions: `Namespace` `rook-ceph`, `RoleBinding` `rook-ceph-cluster-mgmt`, `RoleBinding` and `Role` `rook-ceph-cmd-reporter`, service accounts `rook-ceph-cmd-reporter` and `rook-ceph-default`, and permissions over pods/configmaps.
Control flow: applying the manifest prepares RBAC and service accounts that Rook uses to manage external-cluster resources and command reporting in the consumer namespace. State persists in Kubernetes RBAC objects. Dependencies are existing ClusterRole `rook-ceph-cluster-mgmt`, operator service account namespace alignment, and Rook CRDs/operator install order. Risks: namespace comments must be substituted consistently, duplicate instructions in the header can confuse apply order, and RBAC over pods/configmaps is intentionally broad for command reporting. Test signals: rolebindings resolve valid subjects/roles, service accounts exist, and external CephCluster reconciliation does not fail RBAC checks.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/common-external.yaml -->

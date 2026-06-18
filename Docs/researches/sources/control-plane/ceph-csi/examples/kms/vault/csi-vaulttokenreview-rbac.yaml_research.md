# sources/control-plane/ceph-csi/examples/kms/vault/csi-vaulttokenreview-rbac.yaml

Purpose: RBAC setup that permits Vault Kubernetes auth token review for Ceph-CSI KMS tests.

Important fields and flow: creates ServiceAccount `rbd-csi-vault-token-review`, ClusterRole permitting `authentication.k8s.io` `tokenreviews` create/get/list, and ClusterRoleBinding binding that role to the service account in `default`.

State, dependencies, and integration: cluster-scoped RBAC and a service account used by Vault init and tenant setup jobs so Vault can validate Kubernetes service account tokens.

Risks and test signals: namespace is hard-coded to `default`, so non-default deployments need adjustment. Excess verbs are broader than minimal token review create. Successful Vault auth setup validates the RBAC.

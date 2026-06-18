# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-serviceaccount.yaml

Purpose: optionally creates the RBD provisioner service account.

Important APIs/types/functions: gated by `.Values.serviceAccounts.provisioner.create`; named by `ceph-csi-rbd.serviceAccountName.provisioner`; labeled with app/chart/component/release/heritage/common labels.

Control flow: the provisioner Deployment uses this identity for all driver and sidecar Kubernetes API calls.

State and persistence behavior: namespace-scoped Kubernetes identity object.

Dependencies and integration points: ClusterRoleBinding, RoleBinding, projected KMS tokens, and pod `serviceAccountName`.

Risks: disabling creation requires a preexisting account with matching RBAC. Shared accounts inherit broad provisioner privileges.

Test signals: pod admission and authorization behavior.

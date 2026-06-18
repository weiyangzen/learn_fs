## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: provides the initial controller ServiceAccount, ClusterRole, and ClusterRoleBinding for the SMB external provisioner in chart v0.2.0.

Important permissions include PV create/patch/delete, PVC get/list/watch/update, StorageClass get/list/watch, events create/update/patch, and secret get. State is cluster-scoped RBAC plus namespace service account. Dependencies are provisioner sidecar requirements and fixed names such as `smb-external-provisioner-role`. Risks include broad cluster scope, fixed name collisions, no resizer permissions, and secret read exposure. Test signal is whether dynamic provisioning succeeds without RBAC denial.

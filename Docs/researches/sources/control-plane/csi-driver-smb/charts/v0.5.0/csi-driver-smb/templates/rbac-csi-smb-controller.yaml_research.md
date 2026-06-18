## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders the v0.5.0 external provisioner RBAC. It remains a provisioner-only role/binding plus service account.

State is cluster-level RBAC. Dependencies are csi-provisioner v2.0.4 permissions and fixed names. Risks include no resizer RBAC, broad secret get, and cluster role collisions. Test signal is dynamic provisioning API access.

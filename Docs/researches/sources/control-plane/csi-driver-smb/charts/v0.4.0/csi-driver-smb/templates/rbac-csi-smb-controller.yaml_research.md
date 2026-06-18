## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders v0.4.0 provisioner RBAC. It creates the controller service account, external provisioner role, and binding.

State is cluster RBAC and namespace service account. Dependencies are fixed resource names and provisioner sidecar needs. Risks include broad secret get, cluster-wide permissions, no resizer permissions, and collisions with other installations. Test signal is absence of RBAC denial during dynamic provisioning.

## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders the v0.3.0 provisioner ServiceAccount and RBAC. It remains focused on the external provisioner and does not include later resizer or node-secret roles.

Important state is cluster-scoped provisioner ClusterRole/Binding and namespace ServiceAccount. Dependencies are fixed names and provisioner permissions. Risks include name collisions, broad secret get, and missing permissions for newer sidecars/features. Test signal is provisioning API access in v0.3.0 deployments.

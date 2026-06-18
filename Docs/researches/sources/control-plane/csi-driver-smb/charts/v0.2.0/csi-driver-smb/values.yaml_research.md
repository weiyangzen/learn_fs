## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/values.yaml

Purpose: expands v0.1.0 values with controller and provisioner configuration. It defines SMB, csi-provisioner, liveness probe, and registrar images; service account names; and Linux/Windows enablement.

State is declarative chart input. Dependencies are Microsoft-hosted image repositories and sidecar versions. Risks include old image registries, limited scheduling/resource customization, and no resizer or feature toggles. Test signal is Helm render and v0.2.0 provisioning behavior.

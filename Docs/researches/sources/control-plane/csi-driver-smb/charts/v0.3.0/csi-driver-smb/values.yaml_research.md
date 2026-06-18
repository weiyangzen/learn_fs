## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/values.yaml

Purpose: supplies v0.3.0 chart defaults: SMB image `v0.3.0`, csi-provisioner v1.4.0, livenessprobe v1.1.0, node-driver-registrar v1.2.0, service account names, and Linux/Windows enablement.

State is declarative input. Dependencies are legacy Microsoft image locations and early sidecar CLIs. Risks include minimal configurability, no resource requests/limits, no resizer, and old registry dependencies. Test signal is Helm render/install and basic provisioning.

## sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/values.yaml

Purpose: contains the minimal defaults for the first SMB CSI chart. It sets the SMB image repository/tag, liveness probe image/tag, node-driver-registrar image/tag, and booleans for Linux and Windows enablement.

State is declarative chart input. Dependencies are legacy Microsoft image registries and sidecar versions `v1.1.0` and `v1.2.0`. Risks include no controller/provisioner values in this release, no resource settings, old image locations, and Windows/Linux defaults that may not match modern clusters. Test signal is historical Helm render/install.

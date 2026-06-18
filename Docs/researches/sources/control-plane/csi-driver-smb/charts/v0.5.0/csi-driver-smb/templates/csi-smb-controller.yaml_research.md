## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the v0.5.0 SMB controller Deployment. The main chart evolution is sidecar image migration to registry.k8s.io-era versions and liveness flag change from connection-timeout to probe-timeout.

Important behavior: provisioner, liveness probe, and SMB controller share `/csi/csi.sock`, use controller service account, and run on Linux. State is controller Deployment and socket volume. Dependencies include csi-provisioner v2.0.4 and livenessprobe v2.1.0. Risks include no resizer, fixed names/ports, privileged SMB container, and compatibility with provisioner v2 flags. Test signal is dynamic provisioning and liveness health.

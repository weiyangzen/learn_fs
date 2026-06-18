## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the v0.4.0 Linux node DaemonSet. It includes early support for chart-level node settings such as rolling update maxUnavailable.

Important behavior: deploys liveness probe, registrar, and privileged SMB plugin, with health port 29643 and kubelet hostPath mount propagation. State is node pods and host plugin/registration directories. Dependencies are sidecar values and privileged Linux mounts. Risks include old liveness flag syntax, hard-coded driver/path details, no resource controls, and old image registry defaults. Test signal is node registration and mount operations.

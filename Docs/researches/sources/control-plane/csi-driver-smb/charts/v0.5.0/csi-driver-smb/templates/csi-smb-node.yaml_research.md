## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the v0.5.0 Linux node DaemonSet. It updates sidecar image versions and liveness probe flags while retaining the early chart structure.

Important behavior: liveness probe, node-driver-registrar, and privileged SMB plugin run on Linux, with kubelet/plugin hostPath mounts and health port 29643. State is node pod and kubelet mount state. Dependencies include livenessprobe v2.1.0, registrar v2.0.1, and privileged host access. Risks include no resource controls, no stats/Kerberos feature flags, and fixed paths/names. Test signal is node registration and mount success.

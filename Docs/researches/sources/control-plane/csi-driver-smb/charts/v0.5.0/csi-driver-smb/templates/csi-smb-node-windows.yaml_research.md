## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.5.0 Windows node DaemonSet using non-HostProcess containers and CSI Proxy named pipes.

Important behavior: liveness probe now uses sidecar v2 style `--probe-timeout`, registrar v2.0.1 registers the driver, and SMB plugin mounts kubelet paths plus CSI Proxy pipes. State includes Windows host paths and DaemonSet pods. Dependencies are registry.k8s.io sidecars, Microsoft SMB image, and CSI Proxy. Risks include beta CSIDriver, fixed kubelet path, no HostProcess support, and pipe compatibility. Test signal is Windows node registration and mount health.

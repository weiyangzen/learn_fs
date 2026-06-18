## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.6.0 Windows node DaemonSet. It is the non-HostProcess CSI Proxy based mode, with a notable change toward configurable Windows kubelet path via `.Values.kubelet.windowsPath` in the registrar path.

Important behavior: liveness probe and registrar run sidecar v2 images, SMB plugin receives endpoint and node id, and hostPath/named pipe mounts connect to kubelet and CSI Proxy. State is Windows node pods, plugin registration paths, and pipe mounts. Dependencies are Windows kubelet path values, CSI Proxy, and v0.6.0 SMB image. Risks include path value mismatch, no HostProcess support, beta CSIDriver, and old pipe compatibility. Test signal is Windows e2e/node readiness.

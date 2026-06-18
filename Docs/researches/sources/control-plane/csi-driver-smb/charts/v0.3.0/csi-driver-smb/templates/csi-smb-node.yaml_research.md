## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the v0.3.0 Linux node DaemonSet. It uses health port 29643 and otherwise follows the early node deployment pattern.

Important behavior: liveness probe, registrar, and privileged SMB plugin share the kubelet plugin socket and mount host kubelet directories with bidirectional propagation. State is node plugin pods and hostPath directories. Dependencies are sidecar images from values and privileged Linux node access. Risks include fixed names/ports, old flags, no resource defaults, and no optional Kerberos or stats features. Test signal is Linux node plugin readiness and mount success.

## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.2.0 Windows node DaemonSet. It remains the non-HostProcess, CSI Proxy pipe based deployment.

Important behavior: liveness probe, node-driver-registrar, and SMB plugin use hard-coded kubelet paths and driver name, health port 39613, and Windows node selector. State includes host paths and CSI Proxy pipe mounts. Dependencies are old sidecar images and CSI Proxy beta interfaces. Risks include hard-coded paths, old flags, no configurable resources, and dependency on removed beta pipe names. Test signal is Windows node plugin registration and mounts in v0.2.0 environments.

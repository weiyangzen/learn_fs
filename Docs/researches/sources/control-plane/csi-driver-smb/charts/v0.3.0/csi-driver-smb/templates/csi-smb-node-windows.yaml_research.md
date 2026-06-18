## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.3.0 Windows node DaemonSet. Compared with earlier charts, the health port aligns to 29643, but deployment remains CSI Proxy pipe based.

Important behavior: Windows liveness probe, registrar, and SMB plugin use hard-coded paths and driver name; SMB plugin receives endpoint and node id. State includes Windows hostPath/plugin directories and CSI Proxy pipe mounts. Dependencies are old sidecars and Windows CSI proxy. Risks include old beta API/pipes, no HostProcess mode, fixed paths, and sparse configuration. Test signal is Windows node registration and mount behavior.

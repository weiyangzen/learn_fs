## sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the original Windows SMB node DaemonSet for chart v0.1.0 when Windows is enabled. It predates HostProcess support and relies on Windows containers plus CSI Proxy named pipes.

Important behavior: deploys liveness probe, node-driver-registrar, and SMB plugin with hard-coded driver name/socket paths under `C:\var\lib\kubelet`, health port 39613, and v1beta1 CSI Proxy pipe mounts. Image tags come from the compact v0.1.0 values file.

State is Windows DaemonSet pods, kubelet plugin host paths, and named pipe mounts. Dependencies include early sidecar versions, CSI Proxy beta pipes, and Kubernetes Windows CSI support. Risks include removed beta APIs/pipes, no configurable kubelet path, hard-coded ports, and no HostProcess mode. Test signal is historical Windows node registration/mount behavior.

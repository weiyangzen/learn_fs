## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the legacy/non-HostProcess Windows SMB node DaemonSet when Windows is enabled and `.Values.windows.useHostProcessContainers` is false.

Important behavior: it runs liveness probe, node-driver-registrar, and `smb` containers using Windows paths under `C:\csi` and kubelet plugin directories. The SMB container mounts kubelet directories and CSI Proxy named pipes for filesystem and SMB APIs, including v1 and v1beta1 compatibility pipes, and exposes a health endpoint.

State includes hostPath mounts, named pipe mounts, plugin socket paths, and Windows DaemonSet pods. Dependencies include external CSI Proxy availability, Windows kubelet path, service account, and sidecar images. Risks include CSI Proxy pipe compatibility, hostPath path escaping, security context limitations on Windows, and needing `.Values.windows.csiproxy.enabled` or a manually installed proxy. Test signal is Windows mount/unmount e2e coverage.

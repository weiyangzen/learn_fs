## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml

Purpose: renders the preferred Windows node DaemonSet when Windows support and HostProcess containers are enabled. It runs the SMB plugin directly on the host network as `NT AUTHORITY\SYSTEM`.

Important behavior: an init container creates the kubelet plugin directory, then `node-driver-registrar` registers the CSI socket and `smbplugin.exe` runs with node id, driver name, get-volume-stats, remove-mapping, and `--enable-windows-host-process=true`. It selects Windows nodes, uses HostProcess security context, release service account, pull secrets, and Windows-specific resources.

State is host-level plugin socket directories and DaemonSet pods. Dependencies include Windows HostProcess support, image tag with `-windows-hp`, kubelet path values, and RBAC/service account. Risks include high host privilege, path escaping mistakes, no liveness probe sidecar in this mode, and image tag coupling to release pipeline. Test signal is Windows e2e and Helm render/install.

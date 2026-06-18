<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

- Purpose: Helm template for the v1.8.0 Windows node DaemonSet. It installs the SMB CSI node plugin on Windows workers using node-driver-registrar, liveness-probe, and CSI proxy pipe mounts.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.windows.enabled` is true. It consumes `.Values.windows.kubelet`, `.Values.windows.removeSMBMappingDuringUnmount`, `.Values.node`, `.Values.driver.name`, and image settings for the registrar, liveness probe, and SMB plugin.
- Control flow: the liveness probe checks the Windows CSI socket, node-driver-registrar registers the plugin path under the kubelet plugin registry, and the `smb` process runs with `--endpoint`, `--nodeid`, `--metrics-address`, `--enable-get-volume-stats`, and the Windows unmount cleanup flag.
- State and persistence behavior: the DaemonSet binds the Windows kubelet directory, plugin directory, registration directory, and CSI proxy named pipes. Persistent data lives on the SMB share; local state is sockets, plugin registration files, and transient mount mappings.
- Dependencies/integration points: requires Windows nodes, kubelet host paths, CSI proxy filesystem and SMB APIs, Kubernetes fieldRef for `spec.nodeName`, and the node ServiceAccount/RBAC from the chart. It also carries beta CSI proxy pipe compatibility in these versions.
- Risks: incorrect Windows path escaping can break registration, missing CSI proxy pipes prevents mount/unmount calls, and stale SMB mappings can survive unmount if the cleanup flag is disabled or unsupported. HostPath and named-pipe access are high-trust integrations.
- Test signals: verify via `helm template` on a Windows-enabled values file, node-driver-registrar liveness, kubelet plugin registration, and an SMB PVC mounted by a Windows workload.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

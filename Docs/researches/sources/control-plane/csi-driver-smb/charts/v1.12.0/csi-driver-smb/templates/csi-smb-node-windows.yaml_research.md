<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.12.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts both GA v1 and beta v1beta1 csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-node.yaml

Purpose: Deploys the v4.13.2 NFS CSI node plugin as a system-node-critical DaemonSet. It registers the driver with kubelet and performs node-side NFS publish/unpublish operations.

Important APIs and types: The DaemonSet uses `hostNetwork: true`, `dnsPolicy: ClusterFirstWithHostNet`, ServiceAccount `csi-nfs-node-sa`, `priorityClassName: system-node-critical`, `RuntimeDefault` seccomp, Linux node selector, all-taint toleration, and rolling update `maxUnavailable: 1`. Containers are `livenessprobe:v2.17.0`, `csi-node-driver-registrar:v2.15.0`, and `nfsplugin:v4.13.2`. The registrar has `--csi-address=/csi/csi.sock` and `--kubelet-registration-path=/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`; v4.13.2 adds registrar `--timeout=60s` compared with v4.13.1. The NFS plugin is privileged, adds `SYS_ADMIN`, drops other capabilities, allows privilege escalation, mounts the plugin socket hostPath and `/var/lib/kubelet/pods` with bidirectional propagation, and serves health on localhost port 29653.

Control flow: The NFS plugin creates the CSI socket in the kubelet plugin directory. The registrar registers the driver name/path with kubelet. Kubelet calls the node CSI service to mount NFS volumes into pod directories, using the StorageClass/PV attributes prepared by the controller. Liveness probes watch the CSI socket and driver health endpoint.

State and persistence behavior: Socket and registration artifacts live on hostPath directories and are recreated by the DaemonSet. Volume mount state is node-local under kubelet pod directories; data persists remotely on NFS. The DaemonSet keeps one pod per eligible node and rolls updates one unavailable node at a time.

Dependencies and integration points: Requires the `CSIDriver` object, matching controller side, host kubelet paths, NFS client support, and cluster DNS/network access to NFS exports. It integrates with kubelet through `/var/lib/kubelet/plugins_registry` and with pod volume lifecycle through mount propagation.

Risks: High privilege is inherent to mount management. Broad toleration can place the plugin on nodes where NFS is blocked or unsupported. The registrar timeout bounds registration calls, but too-short timeouts could expose slow kubelet or filesystem behavior during startup. HostPath paths assume a standard kubelet root.

Test signals: Check DaemonSet readiness on each node, `CSINode` driver registration, registrar logs, liveness endpoint on port 29653, pod mount/unmount, and node reboot or plugin restart recovery. Include tests with service DNS NFS endpoints and tainted nodes.

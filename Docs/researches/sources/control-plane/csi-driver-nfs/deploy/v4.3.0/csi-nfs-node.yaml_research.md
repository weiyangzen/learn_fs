## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-node.yaml

Purpose: Deploys the v4.3.0 NFS CSI node plugin as a Linux DaemonSet. It updates node sidecar versions, switches host-network DNS to `ClusterFirstWithHostNet`, and sets pod-level seccomp defaults.

Important APIs and types: The DaemonSet uses rolling updates, `hostNetwork: true`, `dnsPolicy: ClusterFirstWithHostNet`, ServiceAccount `csi-nfs-node-sa`, `priorityClassName: system-node-critical`, `RuntimeDefault` seccomp, Linux node selector, and all-taint toleration. Containers are `livenessprobe:v2.10.0`, `csi-node-driver-registrar:v2.8.0`, and `nfsplugin:v4.3.0`. The registrar still uses kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` and an exec liveness probe. The driver is privileged with `SYS_ADMIN`, uses hostPath socket and pods directories, and exposes health port 29653.

Control flow: The node plugin serves CSI over the host plugin socket. The registrar advertises the driver to kubelet via `/registration`. Kubelet invokes node operations for pods, and the liveness sidecar/driver health probe monitor the local endpoint.

State and persistence behavior: Runtime socket and registration state live on hostPath directories under `/var/lib/kubelet`; mounts and pod volume bind points live under `/var/lib/kubelet/pods`. Remote data persists on the NFS server. Kubernetes stores desired DaemonSet rollout state.

Dependencies and integration points: Requires `csi-nfs-driverinfo.yaml`, controller provisioned PVs, kubelet plugin registry support, Linux/NFS mount support, and RBAC ServiceAccount creation. Cluster-aware DNS is important for NFS server names that are Kubernetes services.

Risks: Privileged mount access and broad node toleration run this pod on all Linux nodes, including tainted nodes. Registrar exec liveness can fail if registrar flags change. Any mismatch between `DRIVER_REG_SOCK_PATH` and the `socket-dir` hostPath prevents kubelet registration. HostPath assumptions are kubelet-layout specific.

Test signals: Confirm DaemonSet rollout, node plugin registration in `CSINode`, successful pod mount/unmount, liveness probe stability, and DNS resolution of service-backed NFS servers from host-networked node pods.

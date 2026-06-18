# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: 4.11.0 node DaemonSet.

Important APIs/types/functions: Same structure as v4.10.0: livenessprobe, node-driver-registrar, privileged NFS, kubeletDir hostPaths, serviceAccount.node, image baseRepo handling, and optional host NFS config mounts.

Control flow: Host-networked Linux DaemonSet registers the CSI socket, provides health checks, and runs node mount service. Host NFS config mounts render only when propagation feature is true.

State and persistence: Node-local socket, registration, and pod mount state.

Dependencies and integration points: Kubelet plugin registry, CSIDriver, node RBAC identity, and host NFS client config.

Risks: Privileged hostPath access and optional host config propagation. Test signals: rollout, kubelet registration, mount/unmount workload.

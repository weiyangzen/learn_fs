# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v3.1.0 node DaemonSet with mount-permission support.

Important APIs/types/functions: `DaemonSet`; containers livenessprobe, node-driver-registrar, NFS; NFS arg `--mount-permissions`; hostPath socket, pod, and registration volumes.

Control flow: Host-networked Linux DaemonSet registers the CSI socket with kubelet, probes health, and runs the NFS node service. Socket and pod mounts use bidirectional propagation.

State and persistence: Per-node socket and registration files under kubelet directories, plus mounted NFS volume state under pod paths.

Dependencies and integration points: Kubelet plugin registry, CSINode, CSIDriver, and StorageClass/PVC volume consumers.

Risks: Hard-coded kubelet path and privileged mount access remain. Mount permission defaults in values are octal-like and should be validated after rendering. Test signals: rollout, registration probe, and mounted file mode checks.

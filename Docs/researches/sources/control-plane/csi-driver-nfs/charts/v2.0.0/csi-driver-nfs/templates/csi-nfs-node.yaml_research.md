# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: Node DaemonSet for v2.0.0 CSI NFS.

Important APIs/types/functions: Kubernetes `DaemonSet`; containers `node-driver-registrar` and privileged `nfs`; hostPath volumes for plugin, pods, and plugin registry.

Control flow: Runs on every Linux node using host networking. The registrar removes stale registration files in a lifecycle hook, registers `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, and the NFS container exposes the CSI endpoint.

State and persistence: Persists socket/registration artifacts and bidirectional pod mount propagation through kubelet host paths.

Dependencies and integration points: Integrates with kubelet plugin registration and per-node volume mount/unmount operations.

Risks: Hard-coded kubelet paths, privileged hostPath access, and no separate node service account in this version. Test signals: DaemonSet readiness, `CSINode` entries, and pod volume mount tests.

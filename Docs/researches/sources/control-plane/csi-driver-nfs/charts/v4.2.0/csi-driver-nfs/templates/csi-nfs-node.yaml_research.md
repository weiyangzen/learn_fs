# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template renders the v4.2.0 node DaemonSet that registers and runs the NFS CSI node plugin.

## Important APIs, Types, and Functions
It emits an `apps/v1` `DaemonSet` with liveness probe, node-driver-registrar, and privileged NFS plugin containers. It mounts kubelet plugin, pod, and registration host paths. The registrar uses an exec liveness probe invoking `/csi-node-driver-registrar --mode=kubelet-registration-probe`.

## Control Flow, State, and Persistence
The DaemonSet uses host networking, controller DNS policy, a hard-coded `csi-nfs-node-sa` service account, optional scheduling values, and rolling update max unavailable. Host state includes CSI sockets, plugin registration files, and pod volume mounts.

## Dependencies and Integration Points
It depends on RBAC creating the expected node service account, kubelet directories under `.Values.kubeletDir`, and a matching `CSIDriver`. It integrates with kubelet through the plugin registry and with workloads through bidirectional pod mount propagation.

## Risks and Test Signals
Risks include hard-coded service account use, older exec-based registrar probe, controller DNS policy reuse, privileged `SYS_ADMIN`, and kubelet directory mismatch. Signals are DaemonSet rollout, CSINode driver entries, registrar probe health, pod mount/unmount tests, and rendering with custom kubelet paths.

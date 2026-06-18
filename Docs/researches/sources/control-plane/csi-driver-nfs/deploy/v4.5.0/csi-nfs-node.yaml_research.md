# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-node.yaml

## Purpose
This manifest deploys the v4.5.0 NFS CSI node DaemonSet. It updates the node-side sidecars and NFS plugin image from v4.4.0 while preserving the same kubelet registration and mount behavior.

## Important APIs, Types, and Functions
The `DaemonSet` is `csi-nfs-node` in `kube-system` with rolling update `maxUnavailable: 1`, hostNetwork, Linux node selector, broad tolerations, and `system-node-critical` priority. Containers are `livenessprobe:v2.11.0`, `csi-node-driver-registrar:v2.9.0`, and `nfsplugin:v4.5.0`. The registrar points kubelet at `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`; the NFS container uses privileged `SYS_ADMIN`, bidirectional `/var/lib/kubelet/pods`, and health port 29653.

## Control Flow, State, and Persistence
Each node runs one pod that creates the CSI socket in the kubelet plugin hostPath, registers the driver through the plugins registry, and serves node-stage/node-publish calls. Persistent effects are kubelet registration files, CSI sockets, and pod volume mounts; Kubernetes object state is minimal beyond the DaemonSet and pods.

## Dependencies and Integration Points
It depends on kubelet hostPath layout, Linux mount propagation, `CSIDriver` identity, the controller deployment, and image availability for the v4.5.0 driver and sidecars. It uses `csi-nfs-node-sa` created by RBAC.

## Risks and Test Signals
Risks include registrar upgrade behavior, stale sockets during rolling updates, privileged mount operations, and NFS mount failures surfacing only at workload scheduling time. Test signals are every Linux node reporting a ready DaemonSet pod, successful `CSINode` driver advertisement, healthy 29653 probes, and pod-level NFS mount/unmount operations during a rollout.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-node.yaml

## Purpose
Defines the `kube-system/csi-nfs-node` DaemonSet for v4.12.0. It runs one NFS CSI node plugin per Linux node, registers the driver with kubelet, and performs node-stage/node-publish mount operations.

## Important APIs, Types, And Objects
The pod contains `livenessprobe:v2.17.0`, `csi-node-driver-registrar:v2.15.0`, and `nfsplugin:v4.12.0`. The registrar points kubelet at `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` through `--kubelet-registration-path`. The NFS plugin runs privileged with `SYS_ADMIN`, `NODE_ID` from the node name, and `CSI_ENDPOINT=unix:///csi/csi.sock`.

## Control Flow
The DaemonSet schedules on all Linux nodes with broad tolerations and host networking. The NFS plugin creates its CSI socket in the hostPath plugin directory, the registrar creates kubelet plugin registration under `/var/lib/kubelet/plugins_registry`, and the liveness probe checks `localhost:29653`. Mount operations propagate through the bidirectional `/var/lib/kubelet/pods` hostPath.

## State And Persistence Behavior
Runtime socket and registration files live under kubelet host paths. Volume mount state is maintained by kubelet and the host mount table, while Kubernetes workload state remains in API objects. The DaemonSet strategy rolls one unavailable node pod at a time.

## Dependencies And Integration Points
Requires `csi-nfs-node-sa`, the matching `CSIDriver`, kubelet's CSI plugin registry, Linux NFS client support, and the controller-created PVs. It shares the driver name and socket contract with the controller deployment.

## Risks And Edge Cases
Privileged hostPath access and bidirectional mount propagation are powerful. Custom kubelet roots or read-only host paths will break registration or mounts. Host networking is used because existing NFS connections can break otherwise, so port collisions on the health endpoint should be considered. Broad tolerations place the pod on tainted infrastructure nodes too.

## Test Signals
Validate that every node has a ready daemon pod, kubelet reports the CSI driver in `CSINode`, and `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` exists. Mount a PVC on multiple nodes, restart a daemon pod, and verify workloads keep or recover NFS mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-node.yaml -->

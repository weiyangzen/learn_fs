<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-node.yaml

## Purpose
Deploys the v4.9.0 node-side NFS CSI driver as a DaemonSet. Compared with v4.8.0, the relevant behavioral change in this manifest is the `nfsplugin:v4.9.0` image tag.

## Important APIs, Types, and Functions
The DaemonSet contains `liveness-probe`, `node-driver-registrar`, and `nfs` containers. It uses host paths for the CSI plugin socket, kubelet plugin registry, and pod mount directory. The NFS container is privileged, adds `SYS_ADMIN`, and listens on `unix:///csi/csi.sock`.

## Control Flow, State, and Persistence
Each Linux node runs a pod with host networking and `system-node-critical` priority. The registrar registers `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` with kubelet. Node publish/unpublish operations mutate host mount state under `/var/lib/kubelet/pods`, while registration data lives under kubelet plugin host paths.

## Dependencies and Integration Points
It integrates with kubelet CSI registration, Linux NFS mounts, the `CSIDriver` object, service account creation, and controller-created PV volume contexts. Liveness probing uses localhost port `29653`.

## Risks and Test Signals
Risks include privileged host access, stale socket or registry state, registration path mismatch, and mount propagation failures. Signals are ready DaemonSet pods, kubelet registration success, healthy liveness probes, and application pods mounting/unmounting NFS PVs cleanly.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-node.yaml -->

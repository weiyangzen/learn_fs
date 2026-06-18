<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-node.yaml

## Purpose
Defines the v4.13.0 per-node NFS CSI DaemonSet. It registers the driver with kubelet and performs node-side mount operations for NFS CSI volumes.

## Important APIs, Types, And Objects
The containers are `livenessprobe:v2.17.0`, `csi-node-driver-registrar:v2.15.0`, and `nfsplugin:v4.13.0`. The pod uses host networking, `system-node-critical` priority, broad tolerations, runtime-default seccomp, and host paths for plugin socket, pods, and plugin registry.

## Control Flow
The NFS plugin serves CSI at `/csi/csi.sock`, the registrar exposes `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` to kubelet, and kubelet invokes node publish/unpublish operations as pods consume PVCs. Health is probed on `localhost:29653`.

## State And Persistence Behavior
Host socket/registration files and mount table entries are node-local runtime state. Kubernetes persists workload and PV references; NFS data persists on the configured server. DaemonSet rolling update allows one unavailable node pod at a time.

## Dependencies And Integration Points
Depends on kubelet CSI registration paths, Linux NFS utilities, the matching controller version, `CSIDriver`, and PVs provisioned by `nfs.csi.k8s.io`.

## Risks And Edge Cases
Privileged mount operations and bidirectional `/var/lib/kubelet/pods` propagation are required but sensitive. Health endpoint collisions are possible with host networking. Custom kubelet roots require manifest changes. Upgrade from v4.12.x should verify existing mounts survive node pod replacement.

## Test Signals
Check DaemonSet readiness across nodes, `CSINode` registration, socket presence, mount/unmount behavior, rolling update behavior with active pods, and liveness probe stability.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-node.yaml -->

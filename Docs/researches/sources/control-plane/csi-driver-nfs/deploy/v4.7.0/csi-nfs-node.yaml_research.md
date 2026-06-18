<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-node.yaml

## Purpose
Deploys the Linux node-side CSI NFS plugin as a `kube-system` `DaemonSet` for release v4.7.0. It registers `nfs.csi.k8s.io` with kubelet on every tolerated node and runs the NFS CSI node service, node-driver-registrar, and liveness sidecar.

## Important APIs, Types, and Functions
The Kubernetes objects are `apps/v1` `DaemonSet`, hostPath volumes for `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and `/var/lib/kubelet/pods`, plus containers `liveness-probe`, `node-driver-registrar`, and `nfs`. Sidecar images are `livenessprobe:v2.13.1` and `csi-node-driver-registrar:v2.11.1`; the driver image is `registry.k8s.io/sig-storage/nfsplugin:v4.7.0`.

## Control Flow, State, and Persistence
Kubernetes schedules one pod per node with `hostNetwork: true`, `ClusterFirstWithHostNet`, broad tolerations, and `system-node-critical` priority. The driver listens on `/csi/csi.sock`, the registrar publishes that socket to kubelet through `/registration`, and the liveness probe exposes health on localhost port `29653`. Persistent state is host-mounted kubelet plugin registration and pod mount state; the DaemonSet itself uses rolling updates with `maxUnavailable: 1`.

## Dependencies and Integration Points
This manifest integrates with kubelet CSI plugin discovery, kubelet pod volume mount directories, Linux NFS mount support, Kubernetes liveness probing, and the controller/RBAC manifests that create the `csi-nfs-node-sa` service account. The NFS container is privileged and adds `SYS_ADMIN` because mount propagation and NFS operations require host-level mount privileges.

## Risks and Test Signals
Risks include privileged node workload blast radius, dependence on Linux-only host paths, plugin socket path mismatches, hostNetwork policy constraints, and broken mounts if bidirectional propagation is unavailable. Signals are successful DaemonSet rollout, registered `CSINode` driver entries, healthy liveness endpoint on `29653`, kubelet plugin registration success, and successful PVC mount/unmount operations on multiple nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-node.yaml -->

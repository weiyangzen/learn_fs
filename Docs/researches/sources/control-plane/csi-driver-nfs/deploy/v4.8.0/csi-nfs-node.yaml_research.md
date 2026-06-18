<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-node.yaml

## Purpose
Deploys the node-side CSI NFS plugin as a v4.8.0 `DaemonSet`, registering the driver with kubelet and performing node publish/unpublish mount operations.

## Important APIs, Types, and Functions
The manifest defines `csi-nfs-node` in `kube-system` with containers `liveness-probe`, `node-driver-registrar`, and `nfs`. It uses `livenessprobe:v2.13.1`, `csi-node-driver-registrar:v2.11.1`, and `nfsplugin:v4.8.0`. Important paths are `/csi/csi.sock`, `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, `/var/lib/kubelet/plugins_registry`, and `/var/lib/kubelet/pods`.

## Control Flow, State, and Persistence
The DaemonSet runs on all Linux nodes with broad tolerations and host networking. The registrar performs kubelet registration through the host plugin registry, while the privileged NFS container handles mount operations with `SYS_ADMIN` and bidirectional pod mount propagation. HostPath directories persist socket registration and mount state across pod restarts.

## Dependencies and Integration Points
It depends on kubelet CSI plugin registration, Linux NFS client support, service account creation in RBAC manifests, and the `CSIDriver` object. The health endpoint on port `29653` is probed by the liveness sidecar and Kubernetes.

## Risks and Test Signals
Risks include privileged node access, stale plugin sockets, incorrect registration path, missing hostPath directories, and NFS mount propagation failures. Signals are ready DaemonSet pods, successful kubelet registration, `CSINode` driver entries, healthy liveness probes, and successful pod-level NFS volume mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-node.yaml -->

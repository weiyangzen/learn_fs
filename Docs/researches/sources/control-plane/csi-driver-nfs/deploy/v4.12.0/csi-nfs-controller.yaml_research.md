<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-controller.yaml

## Purpose
Defines the `kube-system/csi-nfs-controller` Deployment for the v4.12.0 NFS CSI driver. It runs the CSI controller plugin together with Kubernetes CSI sidecars for provisioning, expansion, snapshots, and liveness.

## Important APIs, Types, And Objects
The pod has five containers sharing `/csi/csi.sock` through an `emptyDir`: `csi-provisioner:v5.3.0`, `csi-resizer:v1.14.0`, `csi-snapshotter:v8.3.0`, `livenessprobe:v2.17.0`, and `nfsplugin:v4.12.0`. Sidecars use `--csi-address=$(ADDRESS)`, leader election in `$(POD_NAMESPACE)`, long CSI timeouts, and bounded retry intervals. The NFS plugin runs privileged with `SYS_ADMIN`, `allowPrivilegeEscalation: true`, `NODE_ID` from `spec.nodeName`, and `CSI_ENDPOINT=unix:///csi/csi.sock`.

## Control Flow
The Deployment starts one controller pod on Linux, with host networking and control-plane tolerations. Sidecars connect to the NFS plugin socket and watch Kubernetes resources: PVC/PV creation, expansion requests, and snapshot objects. The controller plugin mounts NFS and creates backing directories, using `/var/lib/kubelet/pods` mounted bidirectionally for mount propagation. The liveness probe polls the plugin health endpoint on `localhost:29652`.

## State And Persistence Behavior
The pod itself is stateless, but it orchestrates persistent Kubernetes objects and backing NFS directories. Leader election state is stored in `coordination.k8s.io` Lease objects. The CSI socket is ephemeral in `emptyDir`; kubelet pod mount state is accessed through the hostPath mount.

## Dependencies And Integration Points
Requires `rbac-csi-nfs.yaml` service account and roles, the `CSIDriver` object, snapshot CRDs/RBAC for snapshot sidecar operation, and the `StorageClass`/`VolumeSnapshotClass` resources that reference `nfs.csi.k8s.io`.

## Risks And Edge Cases
The controller is privileged, host-networked, and has bidirectional hostPath mount propagation, which is necessary for this driver but broadens node risk. A single replica makes leader election mostly future-proofing rather than HA. Resource requests are very small, so busy provision or snapshot workloads may be throttled. The deployment assumes `/var/lib/kubelet/pods`, which may differ on custom kubelet roots.

## Test Signals
Validate with Kubernetes schema dry-run, then check all containers become ready and `/healthz` responds. Functional tests should create and delete PVCs using `nfs-csi`, expand a PVC, create a snapshot, restore from a snapshot, and confirm sidecar leader-election Leases and event emissions are present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-controller.yaml -->

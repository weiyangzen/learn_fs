<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-controller.yaml

## Purpose
Defines the v4.12.1 `csi-nfs-controller` Deployment. It is functionally the v4.12.0 controller manifest with the NFS plugin image advanced to `nfsplugin:v4.12.1`.

## Important APIs, Types, And Objects
The Deployment runs one host-networked Linux pod using `csi-nfs-controller-sa`. Sidecars are `csi-provisioner:v5.3.0`, `csi-resizer:v1.14.0`, `csi-snapshotter:v8.3.0`, `livenessprobe:v2.17.0`, and `nfsplugin:v4.12.1`. All CSI sidecars communicate through `/csi/csi.sock`.

## Control Flow
Provisioner, resizer, and snapshotter watch Kubernetes storage objects and forward CSI calls over the shared socket to the NFS plugin. The NFS plugin runs privileged, mounts host kubelet pod paths bidirectionally, and exposes health on `localhost:29652`. Leader-election flags coordinate sidecars through namespace Leases.

## State And Persistence Behavior
The Deployment stores no local durable state. Kubernetes PVs, PVC status, snapshot content/status, events, and Leases persist the controller's decisions. The socket is recreated with the pod.

## Dependencies And Integration Points
Requires v4.12.1 RBAC, `CSIDriver`, snapshot CRDs, snapshot controller, and StorageClass/SnapshotClass objects using `nfs.csi.k8s.io`. The image tag is the only source-level change from v4.12.0 in this file.

## Risks And Edge Cases
The same privileged hostPath and hostNetwork risks as v4.12.0 apply. Version skew between sidecars and the v4.12.1 plugin should be validated, especially snapshot and resize calls. Low CPU requests may underrepresent busy controller needs.

## Test Signals
Run provisioning, expansion, snapshot, restore, and delete tests after upgrading from v4.12.0 to verify the plugin-only bump does not change object compatibility. Confirm the running image tag is `v4.12.1` and all sidecars can connect to the socket.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-controller.yaml -->

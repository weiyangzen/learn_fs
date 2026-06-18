## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/rbac-csi-nfs.yaml

Purpose: Creates ServiceAccounts and controller-side permissions for the v4.3.0 NFS CSI deployment, including the newly added CSI snapshotter sidecar permissions.

Important APIs and types: Defines ServiceAccounts `csi-nfs-controller-sa` and `csi-nfs-node-sa`, ClusterRole `nfs-external-provisioner-role`, and binding `nfs-csi-provisioner-binding`. The role can manage PV provisioning, update PVCs, read StorageClasses, read snapshot classes/snapshots, get/list/watch/update/patch `VolumeSnapshotContent`, update/patch content status, write events, read CSINodes/Nodes, manage leases, and get Secrets.

Control flow: The external provisioner uses PV/PVC/StorageClass/event/lease permissions for dynamic provisioning. The `csi-snapshotter` sidecar in the controller uses snapshot permissions to watch snapshot objects/content and update content status around CSI snapshot calls. Both sidecars share the controller ServiceAccount and the `/csi/csi.sock` endpoint exposed by the NFS container.

State and persistence behavior: RBAC persists cluster authorization. It allows sidecars to create/update PV-related and snapshot-content state in the API and leader-election lease state. It does not store driver state itself.

Dependencies and integration points: Requires the v4.3.0 controller deployment with `csi-provisioner` and `csi-snapshotter`, the snapshot CRDs, `rbac-snapshot-controller.yaml`, and `csi-nfs-driverinfo.yaml`. The node ServiceAccount is consumed by the DaemonSet even though node API permissions are implicit/minimal.

Risks: The provisioner PV verbs still lack `patch`, which later v4.13.x adds. There is no resizer ClusterRole because v4.3.0 has no `csi-resizer` sidecar. Snapshot permissions are cluster-wide and must align with installed CRDs; applying before CRDs can still create RBAC, but sidecars will fail until APIs exist. Shared ServiceAccount means provisioner and snapshotter both receive all controller permissions.

Test signals: Verify controller ServiceAccount can watch snapshot resources and update `volumesnapshotcontents/status`, can create/delete PVs, and can manage leases. Create a PVC and snapshot, then inspect PV, VolumeSnapshotContent, and status event updates. Confirm no resize flow is expected for this version.

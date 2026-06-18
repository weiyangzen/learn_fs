<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller.go

## Purpose
This file implements the controller for `CephFilesystemSubVolumeGroup` CRs. It creates, updates, pins, reports, and deletes CephFS subvolume groups, and keeps CSI operator client profile metadata aligned with the subvolume group.

## Important APIs and control flow
`Add` registers a field index on `spec.filesystemName/subvolumeGroupName` and installs the controller. `reconcile` fetches the CR, adds the finalizer, initializes status, waits for a ready `CephCluster`, loads cluster info, handles deletion, detects Ceph version, verifies the referenced `CephFilesystem` is ready, creates or updates the subvolume group, applies pinning through `cephclient.PinCephFSSubVolumeGroup`, updates status to Ready, and creates/updates the CSI client profile. External clusters skip creation/deletion of the Ceph subvolume group but still update status and CSI metadata.

Deletion lists other CRs with the same filesystem/group index. It deletes the Ceph subvolume group only when this is the last CR referencing it. `deleteSubVolumeGroup` treats ENOENT as success and ENOTEMPTY as a guarded failure; if force-delete is requested, it starts a cleanup Job and still returns a wrapped delete error describing cleanup. `cleanup` builds a resource cleanup job configured with subvolume group, filesystem, CSI namespace, and metadata pool. `buildClusterID` returns explicit `spec.clusterID` or a hash of namespace/filesystem/group. `formatPinning` renders status text for export, distributed, random, or default distributed pinning.

## State and persistence
State spans Kubernetes finalizers, CR status, CephFS subvolume groups, CephFS pinning metadata, CSI config/client profile objects, and optional cleanup Jobs. Status stores `Phase`, `ObservedGeneration`, and an info map containing `clusterID` and `pinning`.

## Dependencies and integration points
The controller uses controller-runtime, Rook cluster readiness and finalizer helpers, Ceph CLI client helpers for subvolume group lifecycle and pinning, CSI config helpers, `csiopv1.ClientProfile`, and Rook cleanup-job machinery. It integrates with `CephFilesystem` readiness and external-cluster semantics.

## Risks and test signals
Deletion behavior intentionally avoids deleting shared subvolume groups until the last CR is removed; the field index must match `getSubvolumeGroupName` or shared-reference detection can be wrong. Force cleanup starts asynchronous cleanup but returns an error from deletion, so callers see a failure while cleanup proceeds. Tests cover no-cluster and not-ready requeues, successful creation, external mode CSI update, Multus cluster path, deterministic cluster ID hashing, and pinning formatting.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller.go -->

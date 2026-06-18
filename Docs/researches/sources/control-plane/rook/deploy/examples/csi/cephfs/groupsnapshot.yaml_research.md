<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshot.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshot.yaml

Purpose: example `VolumeGroupSnapshot` for selecting multiple CephFS PVCs into one CSI group snapshot.
Important APIs/types/functions: Kubernetes external snapshotter `groupsnapshot.storage.k8s.io/v1beta1`, `VolumeGroupSnapshot`, label selector `spec.source.selector.matchLabels`, and `volumeGroupSnapshotClassName`.
Control flow: after apply, the group snapshot controller selects PVCs labeled `group: snapshot-test` and asks the CephFS CSI driver through `csi-cephfsplugin-groupsnapclass` to create coordinated snapshots. State is persisted in Kubernetes API objects and in backend CephFS snapshots managed by CSI. Dependencies and integration points are the group snapshot CRDs/controller, matching PVC labels from `pvc.yaml`, and the CephFS group snapshot class. Risks: beta API availability, selector matching the wrong or no PVCs, and class/driver mismatch. Test signals: CRD installed, selected PVCs bound, snapshot class exists, and `VolumeGroupSnapshot.status` reaches ready.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshot.yaml -->

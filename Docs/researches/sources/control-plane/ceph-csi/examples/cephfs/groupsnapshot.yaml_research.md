# sources/control-plane/ceph-csi/examples/cephfs/groupsnapshot.yaml

Purpose: example `VolumeGroupSnapshot` selecting CephFS PVCs by label.

Important fields and flow: creates `new-groupsnapshot-demo-1` with selector `group: test` and class `csi-cephfsplugin-groupsnapclass`. Any PVCs with that label are included by the group snapshot controller.

State, dependencies, and integration: creates a namespace-scoped group snapshot CRD instance and requires the group snapshot CRDs/controller plus `groupsnapshotclass.yaml`.

Risks and test signals: unlabeled PVCs are ignored, and unsupported clusters will reject the CRD. Readiness signals group snapshot controller and CephFS driver support.

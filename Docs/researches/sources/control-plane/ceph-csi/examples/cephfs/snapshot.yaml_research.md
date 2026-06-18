# sources/control-plane/ceph-csi/examples/cephfs/snapshot.yaml

Purpose: example `VolumeSnapshot` for the baseline CephFS PVC.

Important fields and flow: Snapshot `cephfs-pvc-snapshot` uses class `csi-cephfsplugin-snapclass` and source PVC `csi-cephfs-pvc`.

State, dependencies, and integration: creates snapshot CRD state and backend CephFS snapshot through the CSI snapshotter. Used by restore examples and e2e snapshot helpers.

Risks and test signals: requires snapshot CRDs/controller and ready source PVC. `ReadyToUse` status and restore success validate snapshot behavior.

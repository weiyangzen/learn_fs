# sources/control-plane/ceph-csi/examples/cephfs/snapshotclass.yaml

Purpose: example CephFS `VolumeSnapshotClass`.

Important fields and flow: class `csi-cephfsplugin-snapclass` uses driver `cephfs.csi.ceph.com`, placeholder `clusterID`, optional snapshot name prefix, snapshotter secret refs, and `deletionPolicy: Delete`.

State, dependencies, and integration: cluster-scoped snapshot class consumed by `snapshot.yaml`; e2e code injects cluster ID and secret namespace/name.

Risks and test signals: placeholders must be replaced. Delete policy removes backend snapshots when content is deleted. Creation plus snapshot readiness validate snapshotter configuration.

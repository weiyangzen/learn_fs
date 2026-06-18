# sources/control-plane/ceph-csi/examples/cephfs/groupsnapshotclass.yaml

Purpose: example cluster-scoped `VolumeGroupSnapshotClass` for CephFS.

Important fields and flow: uses driver `cephfs.csi.ceph.com`, placeholder `clusterID` and `fsName`, group snapshotter secret name/namespace, and `deletionPolicy: Delete`.

State, dependencies, and integration: configures how group snapshot requests reach the CephFS CSI group snapshotter. E2E code loads this file and injects real cluster ID, filesystem name, and secret namespace/name.

Risks and test signals: placeholders must be replaced before real use. Delete policy removes backend snapshots with the class-owned content. Successful creation is required before `groupsnapshot.yaml` can become ready.

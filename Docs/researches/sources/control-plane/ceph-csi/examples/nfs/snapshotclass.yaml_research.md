# sources/control-plane/ceph-csi/examples/nfs/snapshotclass.yaml

Purpose: example NFS `VolumeSnapshotClass`.

Important fields and flow: class `csi-nfsplugin-snapclass` uses driver `nfs.csi.ceph.com`, placeholder `clusterID`, optional snapshot name prefix, CephFS secret refs, and `deletionPolicy: Delete`.

State, dependencies, and integration: configures NFS CSI snapshotter to snapshot the CephFS-backed export.

Risks and test signals: placeholders and secret refs must match deployment. Successful snapshot creation validates the class.

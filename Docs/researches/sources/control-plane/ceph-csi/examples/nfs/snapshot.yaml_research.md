# sources/control-plane/ceph-csi/examples/nfs/snapshot.yaml

Purpose: example NFS `VolumeSnapshot`.

Important fields and flow: Snapshot `nfs-pvc-snapshot` uses class `csi-nfsplugin-snapclass` and source PVC `csi-nfs-pvc`.

State, dependencies, and integration: requests a snapshot of the backing CephFS subvolume/export through NFS CSI.

Risks and test signals: source PVC name differs from baseline `cephcsi-nfs-pvc`, requiring adjustment in some flows. Ready status and restore success validate snapshotting.

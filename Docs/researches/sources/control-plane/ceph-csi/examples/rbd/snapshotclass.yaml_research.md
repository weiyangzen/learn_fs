## sources/control-plane/ceph-csi/examples/rbd/snapshotclass.yaml

Purpose: Example `VolumeSnapshotClass` for RBD CSI snapshots.

Important API surface: `driver: rbd.csi.ceph.com`, required `clusterID`, optional `snapshotNamePrefix`, snapshotter secret name/namespace, and `deletionPolicy: Delete`.

Control flow and state: The external snapshotter passes class parameters and secret references to RBD CSI. The driver resolves the Ceph cluster from `clusterID` and creates/deletes backend snapshots according to Kubernetes snapshot lifecycle.

Dependencies and risks: Requires matching `ceph-csi-config`, `csi-rbd-secret`, snapshot CRDs, and the RBD controller. Placeholder cluster ID must be replaced. `Delete` can remove backend snapshots on object deletion. Test with `snapshot.yaml` and restore manifests.

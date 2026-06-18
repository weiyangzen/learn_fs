## sources/control-plane/ceph-csi/examples/rbd/groupsnapshotclass.yaml

Purpose: Example `VolumeGroupSnapshotClass` for the RBD CSI driver.

Important API surface: `apiVersion: groupsnapshot.storage.k8s.io/v1beta2`, `driver: rbd.csi.ceph.com`, required parameters `clusterID` and `pool`, optional `volumeGroupNamePrefix`, group snapshotter secret name/namespace, and `deletionPolicy: Delete`.

Control flow and state: The Kubernetes group snapshotter passes class parameters and secrets to the RBD CSI controller. Ceph CSI uses the cluster ID to resolve monitors/config and pool for backend group snapshot bookkeeping. Kubernetes stores class state; Ceph stores backend group/snapshot objects.

Dependencies and risks: Requires the `csi-rbd-secret`, valid `ceph-csi-config`, matching pool, and group snapshot sidecars/CRDs. Placeholder values must be replaced. `Delete` deletion policy can remove backend snapshots with the Kubernetes object. Test by creating a `VolumeGroupSnapshot` and checking backend cleanup behavior.

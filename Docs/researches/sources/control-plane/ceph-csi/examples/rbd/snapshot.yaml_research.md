## sources/control-plane/ceph-csi/examples/rbd/snapshot.yaml

Purpose: Example `VolumeSnapshot` for the baseline RBD PVC.

Important API surface: `snapshot.storage.k8s.io/v1`, `VolumeSnapshot` named `rbd-pvc-snapshot`, `volumeSnapshotClassName: csi-rbdplugin-snapclass`, and source `persistentVolumeClaimName: rbd-pvc`.

Control flow and state: The snapshot controller invokes RBD CSI `CreateSnapshot`; Kubernetes stores snapshot CR state and Ceph stores the backend image snapshot. This snapshot is used by restore PVC examples.

Dependencies and risks: Requires snapshot CRDs/controller, `snapshotclass.yaml`, bound source PVC, and Ceph CSI snapshot capability. Deleting the object may delete backend snapshot because class policy is `Delete`. Test by applying and verifying `readyToUse` before restore.

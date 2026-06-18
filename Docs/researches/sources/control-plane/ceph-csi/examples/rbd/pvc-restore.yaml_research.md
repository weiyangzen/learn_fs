## sources/control-plane/ceph-csi/examples/rbd/pvc-restore.yaml

Purpose: Example filesystem PVC restored from an RBD `VolumeSnapshot`.

Important API surface: PVC `rbd-pvc-restore`, `storageClassName: csi-rbd-sc`, data source `VolumeSnapshot` named `rbd-pvc-snapshot`, API group `snapshot.storage.k8s.io`, `ReadWriteOnce`, and `1Gi`.

Control flow and state: The snapshot controller/provisioner passes snapshot identity to the RBD CSI controller, which creates a new image initialized from the snapshot and binds a PV.

Dependencies and risks: Requires source snapshot, snapshot class, snapshot CRDs/controller, and a valid storage class. Size and volume mode must be compatible with the source. Test using `pod-restore.yaml` and data comparison against the source snapshot.

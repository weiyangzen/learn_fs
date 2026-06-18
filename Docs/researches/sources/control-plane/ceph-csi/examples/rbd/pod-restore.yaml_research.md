## sources/control-plane/ceph-csi/examples/rbd/pod-restore.yaml

Purpose: Example nginx Pod mounting a filesystem PVC restored from an RBD `VolumeSnapshot`.

Important API surface: Pod `csi-rbd-restore-demo-pod`, mount path `/var/lib/www/html`, PVC reference `rbd-pvc-restore`, and `readOnly: false`.

Control flow and state: The restore is performed by `pvc-restore.yaml`; this Pod triggers node publish and exercises restored data as a mounted filesystem. State lives in the restored RBD image and Kubernetes volume objects.

Dependencies and risks: Requires snapshot CRDs/controller, snapshot object, snapshot class, and RBD CSI snapshot restore support. Restored PVC size must be valid for the snapshot. Test by creating a source PVC with data, snapshotting, restoring, then checking data from the nginx mount.

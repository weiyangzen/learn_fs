# sources/control-plane/ceph-csi/examples/cephfs/pod-restore.yaml

Purpose: example pod consuming a CephFS PVC restored from a snapshot.

Important fields and flow: Pod `csi-cephfs-restore-demo-pod` runs nginx and mounts PVC `cephfs-pvc-restore` at `/var/lib/www/html`.

State, dependencies, and integration: depends on `pvc-restore.yaml` and snapshot support. E2E restore and upgrade tests use it for checksum validation.

Risks and test signals: restore PVC must be bound before pod readiness. Successful file reads indicate snapshot restore data is usable.

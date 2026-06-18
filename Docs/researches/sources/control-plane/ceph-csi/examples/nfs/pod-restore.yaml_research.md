# sources/control-plane/ceph-csi/examples/nfs/pod-restore.yaml

Purpose: example pod for an NFS PVC restored from snapshot.

Important fields and flow: Pod `csi-nfs-restore-demo-pod` mounts PVC `nfs-pvc-restore` at `/var/lib/www`.

State, dependencies, and integration: pairs with `pvc-restore.yaml` and NFS snapshot support.

Risks and test signals: snapshot restore PVC must be ready. Successful pod access validates restored export mount.

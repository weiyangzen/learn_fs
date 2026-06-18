# sources/control-plane/ceph-csi/examples/cephfs/pod-rwop.yaml

Purpose: example pod consuming a CephFS `ReadWriteOncePod` PVC.

Important fields and flow: Pod `csi-cephfs-demo-rwop-pod` mounts PVC `csi-cephfs-rwop-pvc` at `/var/lib/www`.

State, dependencies, and integration: works with `pvc-rwop.yaml` and tests Kubernetes RWOP access-mode behavior for CephFS.

Risks and test signals: RWOP requires sufficient Kubernetes feature support; helper `rwopMayFail` handles older clusters. Pod startup signals exclusive pod-level write access works.

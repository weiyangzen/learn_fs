# sources/control-plane/ceph-csi/examples/nfs/pod-rwop.yaml

Purpose: example pod consuming an NFS `ReadWriteOncePod` PVC.

Important fields and flow: Pod `csi-nfs-demo-rwop-pod` mounts PVC `csi-nfs-rwop-pvc` at `/var/lib/www`.

State, dependencies, and integration: paired with `pvc-rwop.yaml` for access mode tests.

Risks and test signals: RWOP support depends on Kubernetes version/features. Pod readiness validates exclusive pod-level use through NFS CSI.

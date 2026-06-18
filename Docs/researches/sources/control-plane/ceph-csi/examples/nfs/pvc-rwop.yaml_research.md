# sources/control-plane/ceph-csi/examples/nfs/pvc-rwop.yaml

Purpose: example NFS PVC using `ReadWriteOncePod`.

Important fields and flow: PVC `csi-nfs-rwop-pvc` requests `1Gi` from `csi-nfs-sc` with access mode `ReadWriteOncePod`.

State, dependencies, and integration: used with `pod-rwop.yaml` to validate RWOP behavior.

Risks and test signals: unsupported clusters reject RWOP. Successful bind/mount validates NFS CSI handling.

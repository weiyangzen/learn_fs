# sources/control-plane/ceph-csi/examples/cephfs/pvc-rwop.yaml

Purpose: example CephFS PVC using `ReadWriteOncePod`.

Important fields and flow: PVC `csi-cephfs-rwop-pvc` requests `1Gi` from `csi-cephfs-sc` with access mode `ReadWriteOncePod`.

State, dependencies, and integration: provisions a CephFS volume with pod-exclusive access semantics. Paired with `pod-rwop.yaml`.

Risks and test signals: unsupported clusters reject the access mode. Successful binding/pod start validates RWOP support through CephFS CSI.

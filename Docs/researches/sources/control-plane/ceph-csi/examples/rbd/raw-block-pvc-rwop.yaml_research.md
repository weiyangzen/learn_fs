## sources/control-plane/ceph-csi/examples/rbd/raw-block-pvc-rwop.yaml

Purpose: Example raw block RBD PVC with `ReadWriteOncePod`.

Important API surface: PVC `raw-block-rwop-pvc`, `volumeMode: Block`, `accessModes: ReadWriteOncePod`, `storageClassName: csi-rbd-sc`, and `1Gi` request.

Control flow and state: Dynamic provisioning creates an RBD image and Kubernetes enforces one-Pod access. The PVC is consumed by a Pod through `volumeDevices`.

Dependencies and risks: Requires RWOP support and RBD CSI block support. Testing should confirm both block device publication and single-Pod enforcement; older sidecars may not fully support RWOP.

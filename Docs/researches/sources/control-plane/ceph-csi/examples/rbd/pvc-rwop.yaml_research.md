## sources/control-plane/ceph-csi/examples/rbd/pvc-rwop.yaml

Purpose: Example RBD filesystem PVC using `ReadWriteOncePod`.

Important API surface: PVC `rbd-rwop-pvc`, access mode `ReadWriteOncePod`, `storageClassName: csi-rbd-sc`, and requested storage `1Gi`.

Control flow and state: Dynamic provisioning creates a normal RBD image, while Kubernetes access mode semantics restrict the claim to one Pod at a time. CSI sidecars must advertise/support RWOP semantics.

Dependencies and risks: Requires Kubernetes support for RWOP and compatible sidecars. Older clusters may reject the access mode or not enforce it fully. Test with `pod-rwop.yaml` plus a second consumer to confirm only one Pod can use the claim.

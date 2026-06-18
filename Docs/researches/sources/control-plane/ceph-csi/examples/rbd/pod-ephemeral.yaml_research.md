## sources/control-plane/ceph-csi/examples/rbd/pod-ephemeral.yaml

Purpose: Example Pod using a generic ephemeral RBD PVC template.

Important API surface: Pod `csi-rbd-demo-ephemeral-pod`, `volumes[].ephemeral.volumeClaimTemplate`, `storageClassName: csi-rbd-sc`, `ReadWriteOnce`, and requested size `1Gi`, mounted at `/myspace`.

Control flow and state: Kubernetes creates a lifecycle-bound PVC from the inline template, the RBD provisioner creates a backing image, and the PVC is garbage-collected with the Pod. No separate PVC manifest is needed.

Dependencies and risks: Requires Kubernetes generic ephemeral volume support, Ceph CSI dynamic provisioning, and a valid RBD StorageClass. The storage lifecycle is tied to Pod deletion; data should not be treated as durable beyond the Pod. Test by creating/deleting the Pod and observing PVC/PV/image lifecycle.

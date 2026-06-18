# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csidriver.yaml

Purpose: generated RBD `CSIDriver` object.

Important APIs/types/functions: name `rbd.csi.ceph.com`; `attachRequired: true`, `podInfoOnMount: true`, `seLinuxMount: true`, `fsGroupPolicy: File`.

Control flow: Kubernetes discovers driver capabilities and passes pod info for mount operations.

State and persistence behavior: cluster-scoped object only.

Dependencies and integration points: must match RBD StorageClass provisioner and driver flags.

Risks: direct edits are overwritten by yamlgen. Driver-name mismatch breaks storage class resolution and kubelet registration.

Test signals: RBD CSI discovery, attachment, and pod mount tests.

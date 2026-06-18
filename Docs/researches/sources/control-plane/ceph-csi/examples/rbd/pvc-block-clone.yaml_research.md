## sources/control-plane/ceph-csi/examples/rbd/pvc-block-clone.yaml

Purpose: Example PVC cloning a raw block RBD PVC.

Important API surface: `PersistentVolumeClaim` named `block-pvc-clone`, `storageClassName: csi-rbd-sc`, `volumeMode: Block`, data source kind `PersistentVolumeClaim` named `raw-block-pvc`, `ReadWriteOnce`, and `1Gi` request.

Control flow and state: Kubernetes sends a CSI `CreateVolume` request with a volume content source. The RBD controller creates a clone from the source PVC's RBD image and binds a new PV to this claim.

Dependencies and risks: Requires source PVC to exist and be bound, clone support in the RBD driver, same namespace data source rules, and size not smaller than source. Test by writing to source block PVC, cloning, and verifying copied block contents.

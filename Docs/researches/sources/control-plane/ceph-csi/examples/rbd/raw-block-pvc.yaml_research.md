## sources/control-plane/ceph-csi/examples/rbd/raw-block-pvc.yaml

Purpose: Baseline dynamically provisioned RBD raw block PVC.

Important API surface: PVC `raw-block-pvc`, `volumeMode: Block`, `ReadWriteOnce`, `storageClassName: csi-rbd-sc`, and requested size `1Gi`.

Control flow and state: External provisioning asks the RBD CSI controller for a block-mode image; kubelet later maps it into Pods as a device rather than a mounted filesystem.

Dependencies and risks: Requires valid RBD StorageClass and node plugin support for block devices. Workloads must handle raw device initialization. Test with `raw-block-pod.yaml`, write bytes or create a filesystem, and confirm persistence.

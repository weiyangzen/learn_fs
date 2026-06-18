## sources/control-plane/ceph-csi/examples/rbd/block-pod-clone.yaml

Purpose: Example Pod consuming a cloned RBD block PVC as a raw block device.

Important API surface: A `v1/Pod` named `pod-with-block-volume-clone`, CentOS container, `volumeDevices` entry `devicePath: /dev/xvda`, and a `persistentVolumeClaim` reference to `block-pvc-clone`.

Control flow and integration: Kubernetes schedules the Pod, kubelet calls CSI node stage/publish for the PVC, and the RBD node plugin maps the cloned image as a block device instead of mounting a filesystem. State comes from the PVC/PV binding and mapped device on the node.

Dependencies, risks, tests: Requires `pvc-block-clone.yaml`, the original raw block source PVC, the RBD StorageClass, and node plugin privileges. Device path conflicts or missing `volumeMode: Block` in the PVC are primary risks. Test by creating the source PVC, clone PVC, then verifying `/dev/xvda` exists in the container.

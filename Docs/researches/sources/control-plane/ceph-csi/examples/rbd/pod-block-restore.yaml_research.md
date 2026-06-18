## sources/control-plane/ceph-csi/examples/rbd/pod-block-restore.yaml

Purpose: Example Pod consuming a restored RBD block PVC.

Important API surface: Pod `pod-block-volume-restore` with CentOS container, raw block `volumeDevices` mapping `data` to `/dev/xvda`, and PVC reference `rbd-block-pvc-restore`.

Control flow and state: Kubelet publishes the restored block PVC to the container as a device. The source restoration is defined by `pvc-block-restore.yaml` using a `VolumeSnapshot`; this Pod only validates node-side consumption.

Dependencies and risks: Requires a snapshot object and block restore PVC, RBD CSI block mode support, and privileged node plugin mapping. A filesystem-style PVC would not match `volumeDevices`. Test by writing/reading the block device from inside the container after restore.

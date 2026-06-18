<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/block_volume.yaml -->
# sources/control-plane/longhorn/examples/block/block_volume.yaml

Purpose: demonstrates a Longhorn raw block PVC consumed directly by a pod as a block device.

Important APIs/types/functions: defines a `PersistentVolumeClaim` with `volumeMode: Block`, StorageClass `longhorn`, 2Gi size, and an nginx pod using `volumeDevices` with `devicePath: /dev/longhorn/testblk`.

Control flow: CSI provisions a block-mode Longhorn volume, Kubernetes attaches it to the pod, and kubelet exposes it as the configured device rather than mounting a filesystem.

State and persistence: block data persists in the PVC/Longhorn volume until claim deletion according to StorageClass reclaim policy.

Dependencies/integration points: depends on Longhorn CSI block volume support, RWO attach, kubelet block device mapping, and the default namespace.

Risks/test signals: applications must format/use the raw device correctly; deleting the PVC removes data if reclaim policy is Delete. Test signals are PVC bound, pod running, device present inside container, and read/write block tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/block/block_volume.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pod-ephemeral.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pod-ephemeral.yaml

Purpose: demonstrates a generic ephemeral inline CephFS volume for a single nginx pod.
Important APIs/types/functions: `Pod`, `volumes[].ephemeral.volumeClaimTemplate`, `storageClassName: rook-cephfs`, RWX access mode, and `/myspace` mount.
Control flow: kubelet creates a PVC from the inline template for the pod lifetime; CSI dynamically provisions a CephFS subvolume, mounts it into nginx, and deletes it with the pod. State is intentionally pod-scoped and persisted only for the pod lifetime. Dependencies are Kubernetes generic ephemeral volumes, the CephFS CSI provisioner, and the `rook-cephfs` StorageClass. Risks: cluster version may not support ephemeral volume templates, RWX is unnecessary for one pod but exercises CephFS semantics, and data disappears on pod deletion. Test signals: generated PVC appears, pod reaches Ready, mount is writable, and PVC/backend subvolume are removed after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pod-ephemeral.yaml -->

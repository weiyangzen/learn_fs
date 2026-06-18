<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pod-ephemeral.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pod-ephemeral.yaml

Purpose: demonstrates a generic ephemeral inline RBD volume for an nginx pod.
Important APIs/types/functions: `Pod`, `ephemeral.volumeClaimTemplate`, StorageClass `rook-ceph-block`, RWO access mode, and mount path `/myspace`.
Control flow: kubelet creates a pod-scoped PVC from the template, the RBD CSI provisioner creates an image, and the node plugin maps/formats/mounts it into the container; deletion of the pod removes the generated claim and backend image. State is temporary and tied to pod lifetime. Dependencies are generic ephemeral volume support, RBD CSI provisioner/node plugin, and `rook-ceph-block` StorageClass. Risks: data is deleted with the pod, RBD is single-writer by default, and image mapping needs node kernel/nbd support. Test signals: generated PVC appears, pod Ready, mount writable, and generated PVC/image are cleaned up after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pod-ephemeral.yaml -->

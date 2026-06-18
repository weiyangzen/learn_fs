<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-cr.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-cr.yaml

Purpose: embedded NFS provisioner ClusterRole. It grants node, secret, event, PV/PVC, StorageClass, VolumeAttachment, CSI node, snapshot, and VolumeAttributesClass permissions needed by the external provisioner/snapshotter/attacher surfaces. Rendered into a typed `ClusterRole`. Risk is broad secret list/get access and drift with sidecar requirements; tests only assert unmarshal succeeds.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-cr.yaml -->

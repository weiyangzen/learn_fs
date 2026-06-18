<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/snapshotclass.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/snapshotclass.yaml

Purpose: optional VolumeSnapshotClass template. It sets driver, clusterID, optional snapshotNamePrefix, snapshotter secret name/namespace, labels/annotations, and deletionPolicy. It integrates with snapshot CRDs and snapshotter sidecar. Risk is CRD absence or secret namespace mismatch. Signal is snapshot create/delete success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/snapshotclass.yaml -->

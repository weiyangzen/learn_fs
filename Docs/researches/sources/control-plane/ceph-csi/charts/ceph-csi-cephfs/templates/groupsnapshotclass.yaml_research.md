<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/groupsnapshotclass.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/groupsnapshotclass.yaml

Purpose: optional VolumeGroupSnapshotClass template. When enabled, it sets driver, clusterID, fsName, optional volumeGroupNamePrefix, group snapshotter secret name/namespace, annotations/labels, and deletionPolicy. It integrates with group snapshot CRDs and sidecar feature gates. Risk is CRD absence or secret namespace mismatch; signal is group snapshot creation.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/groupsnapshotclass.yaml -->

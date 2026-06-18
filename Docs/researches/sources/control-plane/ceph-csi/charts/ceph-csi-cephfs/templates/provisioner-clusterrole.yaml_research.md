<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrole.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrole.yaml

Purpose: provisioner ClusterRole template. It grants secrets/configmaps, PV/PVC, storageclasses, events, nodes, snapshot resources, optional group snapshot resources or replication resources, optional attacher permissions, and optional resizer PVC status permissions. It integrates with external-provisioner, snapshotter, attacher, and resizer sidecars. Risk is broad secret access and value-dependent RBAC drift from enabled sidecars. Signals are successful provisioning/snapshot/attach/resize workflows.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrole.yaml -->

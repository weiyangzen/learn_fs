<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/ceph-conf.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/ceph-conf.yaml

Purpose: ConfigMap template for Ceph client config. It names the ConfigMap from `.Values.cephConfConfigMapName`, applies chart/common labels, renders `.Values.cephconf` through `tpl`, and provides an empty keyring. State is Kubernetes ConfigMap data consumed by plugin/provisioner pods. Risk is templated config injection or invalid ceph.conf; Helm lint/render and pod mounts are signals.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/ceph-conf.yaml -->

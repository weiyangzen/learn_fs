<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csiplugin-configmap.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csiplugin-configmap.yaml

Purpose: CSI plugin config ConfigMap template. It is skipped when `.Values.externallyManagedConfigmap` is true and otherwise writes `config.json` from `toJson .Values.csiConfig`. State is cluster config consumed by controller/node pods. Risk is invalid cluster JSON or missing externally managed ConfigMap; signal is pod config mount and driver startup.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csiplugin-configmap.yaml -->

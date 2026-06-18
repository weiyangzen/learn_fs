<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/extra-deploy.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/extra-deploy.yaml

Purpose: pass-through template for arbitrary additional manifests under `.Values.extraDeploy`. It ranges over user-provided objects and renders them with `tpl`. State and dependencies are fully user-defined. Risk is high because arbitrary templated YAML can create any resource; signal is Helm render/apply success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/extra-deploy.yaml -->

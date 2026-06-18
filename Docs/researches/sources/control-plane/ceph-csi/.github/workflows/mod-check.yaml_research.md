<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/mod-check.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/mod-check.yaml

Purpose: module/vendor consistency gate. It runs `make containerized-test TARGET=mod-check`, which tidies, vendors, verifies all modules, and fails on dirty git status. Risk is generated vendor churn; signal is `mod-check`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/mod-check.yaml -->

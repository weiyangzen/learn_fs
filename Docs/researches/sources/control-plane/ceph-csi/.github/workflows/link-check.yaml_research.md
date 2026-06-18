<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/link-check.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/link-check.yaml

Purpose: markdown/link validation. It runs `make containerized-test TARGET=link-check`, which invokes lychee with repo config. Risk is network flake for external links; signal is `link-check`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/link-check.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/codespell.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/codespell.yaml

Purpose: PR spelling gate. It checks out the repository and runs `make containerized-test TARGET=codespell`. It depends on the Makefile test container and scripts/codespell config. Risk is container image freshness; success status is `codespell`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/codespell.yaml -->

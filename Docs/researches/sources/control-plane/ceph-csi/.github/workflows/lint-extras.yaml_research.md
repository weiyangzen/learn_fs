<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/lint-extras.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/lint-extras.yaml

Purpose: non-Go lint aggregate. It runs `make containerized-test TARGET=lint-extras`, covering shell, markdown, YAML, Helm, and Python through scripts. Risk is Helm templates excluded from generic YAML parsing and checked separately; signal is `lint-extras`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/lint-extras.yaml -->

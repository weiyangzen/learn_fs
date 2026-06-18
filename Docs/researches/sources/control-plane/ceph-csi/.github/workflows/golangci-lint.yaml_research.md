<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/golangci-lint.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/golangci-lint.yaml

Purpose: Go lint gate. It checks out code and runs `make containerized-test TARGET=go-lint`, which generates lint config build tags then executes lint script. Risk is mismatch between build tags and CI image; signal is `golangci-lint`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/golangci-lint.yaml -->

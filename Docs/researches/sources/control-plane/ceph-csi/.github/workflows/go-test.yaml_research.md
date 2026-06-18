<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/go-test.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/go-test.yaml

Purpose: Go validation workflow. Jobs check generated deploy code and clean git status, build `e2e.test` in container, run root Go tests, and run API module tests. It integrates with `make generate-deploy`, `check-all-committed`, `containerized-build`, and `containerized-test`. Risk is generated-code drift and container build cost; statuses gate Mergify.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/go-test.yaml -->

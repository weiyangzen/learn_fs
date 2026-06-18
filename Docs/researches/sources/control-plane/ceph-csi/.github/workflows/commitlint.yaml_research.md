<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/commitlint.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/commitlint.yaml

Purpose: PR commit message gate for non-Dependabot PRs. It checks out the head SHA with full history and runs `make containerized-test TARGET=commitlint GIT_SINCE=origin/${GITHUB_BASE_REF}`. Risk is fetch/base-ref history issues; success status is `commitlint`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/commitlint.yaml -->

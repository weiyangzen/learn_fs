<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/dependency-review.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/dependency-review.yaml

Purpose: GitHub dependency-review gate on PRs. It checks out code and runs pinned `actions/dependency-review-action` with one allowed GHSA. It needs contents read permission. Risk is stale allowlist or advisory noise; signal is dependency review status.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/dependency-review.yaml -->

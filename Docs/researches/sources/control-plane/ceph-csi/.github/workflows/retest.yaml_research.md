<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/retest.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/retest.yaml

Purpose: scheduled retry automation for approved PRs. Every 30 minutes in official repo, it runs the local `actions/retest` action with required label `ci/retry/e2e`, max retry 5, and approval count 2. Risk is API rate limits and broad PR scan; signal is generated `/retest` comments.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/retest.yaml -->

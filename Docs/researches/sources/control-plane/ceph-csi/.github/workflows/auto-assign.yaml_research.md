<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/auto-assign.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/auto-assign.yaml

Purpose: issue self-assignment workflow. It triggers on created or edited issue comments and runs pinned `bdougie/take-action` with trigger `/assign`, a thank-you message, and `GITHUB_TOKEN`. It writes assignment state through GitHub APIs only. Risk is action trust/supply-chain despite pinning to a SHA; signal is issue assignee/comment updates.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/auto-assign.yaml -->

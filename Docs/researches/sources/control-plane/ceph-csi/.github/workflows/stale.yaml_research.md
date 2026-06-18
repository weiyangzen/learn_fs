<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/stale.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/stale.yaml

Purpose: daily stale issue/PR management in official repo. It marks issues after 30 days and closes after 7 more; PRs close after 14 stale days; labels such as keepalive/security/reliability/release requirement are exempt. Risk is accidentally closing long-running valid work without labels; signal is stale/wontfix labels and close comments.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/stale.yaml -->

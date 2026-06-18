<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/mergify-copy-labels.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/mergify-copy-labels.yaml

Purpose: copies labels into Mergify merge-queue PRs on `pull_request_target` opened events. It uses a pinned Mergify action, adds `ok-to-test`, and uses `CEPH_CSI_BOT_TOKEN`. Risk is privileged target workflow token exposure if action behavior changes; signal is queue PR labels.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/mergify-copy-labels.yaml -->

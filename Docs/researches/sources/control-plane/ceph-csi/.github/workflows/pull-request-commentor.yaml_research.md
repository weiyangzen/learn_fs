<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/pull-request-commentor.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/pull-request-commentor.yaml

Purpose: starts external Jenkins/e2e jobs when `ok-to-test` is applied. It comments `/test ...` commands for branch-specific Kubernetes versions, upgrade tests, then labels `ci/in-progress/e2e` and removes `ok-to-test`. It uses `pull_request_target` and bot token. Risk is matrix drift against supported branches; signal is comments and label transition.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/pull-request-commentor.yaml -->

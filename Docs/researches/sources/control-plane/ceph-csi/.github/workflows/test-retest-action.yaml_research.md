<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/test-retest-action.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/test-retest-action.yaml

Purpose: PR validation for changes under `actions/retest`. It builds the Docker image from that directory to ensure the local action compiles with its vendored dependencies. Risk is build-only coverage without behavioral tests; signal is Docker build success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/test-retest-action.yaml -->

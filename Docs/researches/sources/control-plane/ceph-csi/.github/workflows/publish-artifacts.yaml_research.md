<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/publish-artifacts.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/publish-artifacts.yaml

Purpose: publishes release/default-branch artifacts for official `ceph/ceph-csi`. On pushes to `devel` or `release-v*`, it logs into Quay, exports bot identity/token env vars, and runs `deploy.sh` with Docker. Risk is secret exposure and Docker-specific build assumptions; signal is successful artifact publishing.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/publish-artifacts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/build-multi-stage.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/build-multi-stage.yaml

Purpose: PR image build validation. It waits one minute for labels, uses `actions/github-script` to detect `ci/skip/multi-arch-build`, then either runs `CONTAINER_CMD=docker ./scripts/build-multi-arch-image.sh` or `make containerized-build`. Concurrency cancels stale runs. Risk is label race and Docker-specific multi-arch behavior; success checks are multi-arch-build or single-arch-build.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/build-multi-stage.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/tickgit.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/tickgit.yaml

Purpose: TODO inventory on pushes to devel. It checks out and runs `make containerized-test TARGET=tickgit`, which scans the repo for tracked TODO markers. Risk is informational failures if tickgit config changes; signal is tickgit job output.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/tickgit.yaml -->

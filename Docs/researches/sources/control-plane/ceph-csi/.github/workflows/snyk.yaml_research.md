<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/snyk.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/snyk.yaml

Purpose: scheduled/tag/release branch Go code vulnerability scan using Snyk. It checks out full history and runs pinned `snyk/actions/golang` with `SYNK_TOKEN`. Risk is token naming typo and Snyk action drift; signal is security scan status.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/snyk.yaml -->

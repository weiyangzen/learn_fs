<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/snyk-container-image.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/snyk-container-image.yaml

Purpose: scheduled/tag/release branch container vulnerability scan. It builds `make image-cephcsi` and runs Snyk Docker action against `quay.io/cephcsi/cephcsi:${{ github.base_ref }}` with Dockerfile path. Risk is base_ref being empty for tag/schedule contexts and secret typo `SYNK_TOKEN`; signal is uploaded scan result.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/snyk-container-image.yaml -->

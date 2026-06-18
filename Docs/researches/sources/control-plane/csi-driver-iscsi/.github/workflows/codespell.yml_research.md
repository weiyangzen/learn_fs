## sources/control-plane/csi-driver-iscsi/.github/workflows/codespell.yml

Purpose: spelling check workflow for csi-driver-iscsi.

Control flow runs on push and pull_request, checks out code, and invokes codespell with filename checks. It skips Git metadata, the workflow, images/checksums, vendor, go.sum, release-tools/prow.sh, and the iSCSI library path, with ignored words for storage-specific terms.

State is workflow run output only. Dependencies are GitHub Actions and codespell action. Risks include broad skip of `./pkg/lib/iscsi/` path that may not match current `pkg/iscsilib`, stale ignore list, and spelling-only coverage. Test signal is workflow pass/fail.

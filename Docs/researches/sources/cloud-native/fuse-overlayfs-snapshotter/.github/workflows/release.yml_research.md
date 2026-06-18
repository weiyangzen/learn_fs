<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/release.yml -->
# sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/release.yml

Purpose: tag-triggered release automation for snapshotter binaries.

Important flow: on `v*` or test release tags, sets up Go 1.24, checks out source, runs `make artifacts`, generates `_output/SHA256SUMS`, records its own checksum, creates a release note, attests build provenance, and creates a draft GitHub release with artifacts.

State and integration: writes GitHub release drafts and provenance attestations. Requires contents, id-token, and attestations permissions. Risks include draft release creation with placeholder notes, reliance on `gh` CLI availability, and artifact naming from Makefile version logic. Test signal is release pipeline execution rather than source tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/release.yml -->

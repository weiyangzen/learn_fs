<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release.yml -->
# sources/cloud-native/overlaybd/.github/workflows/release.yml

Purpose: Multi-distro, multi-architecture release packaging and GitHub release publication.

APIs and control flow: On pushes to `main` and `v*` tags, matrix builds cover Ubuntu 18.04 through 24.04, CentOS 8, CBL-Mariner 2.0, Azure Linux 3.0, and amd64/arm64. Untagged builds derive the next patch `rc`; tagged builds strip the leading `v`. Docker buildx invokes the release Dockerfile with build args, filters irrelevant package type per OS, uploads artifacts, then creates either a prerelease `latest` or tagged release.

State and persistence: Produces `releases/overlaybd-*.*` artifacts and GitHub release assets.

Dependencies and integration: Uses Docker buildx, QEMU, artifact actions, and `marvinpinto/action-automatic-releases`.

Risks and test signals: Version derivation assumes semantic `vX.Y.Z` tags. Package correctness is validated by successful Docker builds, expected RPM/DEB pruning, and uploaded artifact names.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release.yml -->

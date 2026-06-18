# sources/cloud-native/nydus-snapshotter/.github/workflows/release.yml

Purpose: tag-driven release packaging, GitHub release upload, multi-arch image build, and manifest publish.

Flow: builds tarballs for linux amd64/arm64/s390x/ppc64le/riscv64 and static, uploads artifacts, creates a GitHub release, downloads per-arch artifacts into `misc/snapshotter`, builds images with the latest Nydus version, pushes arch tags, then publishes a multi-arch Docker manifest.

State/dependencies: GitHub packages, actions cache/artifacts, cross GCC packages, Docker Buildx/QEMU, Nydus latest release API.

Integration points: ties Makefile packaging to Dockerfile deployment image.

Risks/tests: uses golangci-lint v1.51.2 in release while CI uses v2.1.6. Latest Nydus lookup makes image contents time-dependent.

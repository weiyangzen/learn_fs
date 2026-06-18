<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/build-multi-arch-image.sh -->
## sources/control-plane/ceph-csi/scripts/build-multi-arch-image.sh

Purpose: builds per-architecture Ceph-CSI images using architecture-specific base image digests.

Control flow: sources `build_step.inc.sh`, enables Docker experimental manifest support, reads `BASE_IMAGE` from `build.env`, inspects base image manifests with `docker manifest inspect` and `jq`, starts `multiarch/qemu-user-static`, then loops over `amd64` and `arm64` to run `GOARCH=<arch> BASE_IMAGE=<base>@<digest> make image-cephcsi`.

State and persistence: pushes/builds container image artifacts via Docker/Makefile; changes no repo files directly.

Dependencies: Docker with manifest support, jq, QEMU user static container, `build.env`, Make targets.

Integration points: release/CI image build path for multi-arch output.

Risks: digest extraction via awk over JSON text is brittle compared with jq filtering. Requires privileged Docker run. Only amd64/arm64 are hardcoded.

Test signals: no direct tests; validation is through image build CI.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/build-multi-arch-image.sh -->

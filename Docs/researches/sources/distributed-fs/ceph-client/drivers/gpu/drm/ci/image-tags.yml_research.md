# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/image-tags.yml

Purpose: centralizes the pinned container, kernel rootfs, firmware, and conditional build tags used by DRM CI templates.

Important variables: `CONTAINER_TAG` drives Debian and Alpine build/test image tags. `KERNEL_TAG` and `KERNEL_REPO` select the default kernel/rootfs baseline before the tested kernel is injected. `PKG_REPO_REV`, `FIRMWARE_TAG`, and `FIRMWARE_REPO` pin package and firmware sources. Conditional tags pin ANGLE, crosvm, and Piglit builds, with `CROSVM_TAG` aliased to the conditional crosvm tag.

Control flow: pure GitLab variable data, included by `gitlab-ci.yml` and consumed by freedesktop/Mesa templates and local jobs.

State and persistence: affects container image names and downloaded artifacts; no direct file writes.

Dependencies and integration points: coupled to the sanity job in `gitlab-ci.yml`, which enforces short image tag strings for selected variables, and to `lava-submit.sh` firmware overlay URLs.

Risks: stale tags break reproducibility or can point to unavailable S3 artifacts. Variable names must match upstream template expectations. Long tag values can fail the sanity check.

Test signals: pipeline variable expansion, sanity tag-length pass, container cache hits, rootfs/kernel artifact lookup under `gfx-ci/linux`, and firmware overlay downloads.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/container.yml

Purpose: customizes inherited freedesktop/Mesa container jobs for DRM CI by pointing ci-templates at the DRM CI project cache and specifying extra Debian packages for build and test images while disabling unused inherited containers.

Important sections: `.container` overrides `CI_REPOSITORY_URL` and `CI_COMMIT_SHA` so container templates clone the pinned `DRM_CI_PROJECT_URL`/`DRM_CI_COMMIT_SHA`. `debian/x86_64_build-base` adds kernel/IGT build dependencies such as cairo, elfutils, kmod, pciaccess, proc2, udev, unwind, docutils, bc, ply, and OpenSSL. `debian/arm64_build` adds crossbuild and armhf library variants for arm builds. `debian/*_test-gl` add runtime libraries and `jq` needed by IGT/deqp runner environments. Most other inherited container targets are disabled with `rules: when: never`.

Control flow: this file is data consumed by GitLab's include/extends engine; jobs are built only if selected by rules in `gitlab-ci.yml`.

State and persistence: affects container images tagged through `image-tags.yml`, with no runtime file writes itself.

Dependencies and integration points: depends on freedesktop ci-templates naming conventions and Mesa CI's container hierarchy. Build/test jobs in `build.yml`, `kunit.yml`, and `test.yml` extend these images.

Risks: package names are Debian-release sensitive (`t64` runtime names in test images). The arm64 build image includes armhf cross packages and must stay aligned with `build-igt.sh` arm cross file. Disabled inherited jobs can become stale if upstream template job names change.

Test signals: container pipelines expand only intended Debian build/test images; packages resolve in current Debian base; image tags are short enough for sanity checks; and downstream jobs find required libraries at runtime.

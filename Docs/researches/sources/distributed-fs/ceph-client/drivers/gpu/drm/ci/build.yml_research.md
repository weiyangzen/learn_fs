# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build.yml

Purpose: defines GitLab CI build templates and concrete jobs for DRM kernel builds and IGT builds across arm32, arm64, and x86_64, plus disables unrelated inherited Mesa build jobs.

Important jobs/templates: `.build` runs `drivers/gpu/drm/ci/build.sh` in the `build-only` stage and publishes `artifacts`. `.build:arm32`, `.build:arm64`, and `.build:x86_64` layer architecture-specific containers, runner tags, `DEFCONFIG`, `KERNEL_IMAGE_NAME`, and `KERNEL_ARCH`. `igt:arm32`, `igt:arm64`, and `igt:x86_64` reuse those architecture templates but run `build-igt.sh`. `testing:*` jobs build kernels for hardware tests, enable lockdep/debug Kconfig options, set `UPLOAD_TO_MINIO=1`, and select architecture merge fragments. `build-nodebugfs:arm64` exercises a DEBUG_FS-disabled configuration with MSM XML validation.

Control flow: jobs extend shared `.build-rules` from `gitlab-ci.yml`, so scheduling depends on MR, merge, scheduled, direct-push, and fork conditions. The many inherited Mesa jobs are disabled with `rules: when: never` to keep this kernel CI focused.

State and persistence: produces GitLab artifacts and, for `testing:*`, MinIO artifacts consumed by test jobs. No direct source state changes are made in YAML, but variables configure `build.sh` behavior.

Dependencies and integration points: depends on included Mesa/freedesktop templates for `.use-debian/*` images and runner tags, and on local scripts `build.sh` and `build-igt.sh`. `test.yml`, `check-devicetrees.yml`, and KUnit jobs depend on the build templates and artifacts.

Risks: template names inherited from Mesa CI are external contract points. Disabled jobs must track upstream Mesa job renames or new inherited jobs may appear unexpectedly. Build variables must remain synchronized with architecture handling in `build.sh`.

Test signals: GitLab pipeline expands expected `build:*`, `testing:*`, and `igt:*` jobs; disabled inherited jobs remain skipped; artifacts are available to declared consumers; and `testing:*` jobs upload MinIO objects for LAVA.

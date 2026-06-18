# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/test.yml

Purpose: defines DRM CI test job templates and concrete hardware/software IGT jobs that consume built kernels and IGT artifacts.

Important jobs/templates: `.allow_failure_lockdep` allows exit code 101. `.lava-test` provides common LAVA behavior: build rules, 1h30m timeout, scheduled/collabora/on-success rules, S3 token setup, extracting `artifacts/install.tar`, moving install payload into artifacts, and executing the packaged `lava-submit.sh`. `.lava-igt:*` templates specialize for arm32, arm64, and x86_64 with `HWCI_TEST_SCRIPT=/install/igt_runner.sh`, Debian arch, farm, dependencies on testing kernels, rootfs containers, and IGT build jobs. `.software-driver` runs x86_64 crosvm tests using `install/crosvm-runner.sh install/igt_runner.sh`. Concrete jobs cover MSM boards, Rockchip display and Mali GPUs, i915 Chromebooks, amdgpu Stoney, MediaTek display/Panfrost/Powervr placeholders, Meson display/Panfrost, virtio_gpu, and vkms, with per-device variables for DTB, boot method, firmware, parallel shard count, runner tags, image type, driver name, and GPU version.

Control flow: templates layer through GitLab `extends`, so driver-specific jobs inherit LAVA or crosvm mechanics plus stage labels. Parallel jobs split IGT through `CI_NODE_INDEX` consumed by `igt_runner.sh`. Some devices/jobs are hidden templates or disabled via rules.

State and persistence: consumes kernel/IGT/rootfs artifacts and LAVA/crosvm images; produces results directories and junit through runner scripts and Mesa CI infrastructure.

Dependencies and integration points: depends on `build.sh`, `build-igt.sh`, `igt_runner.sh`, `lava-submit.sh`, Mesa CI LAVA/crosvm templates, lab runner tags, firmware overlays, xfail files, and S3 paths from `gitlab-ci.yml`.

Risks: hardware availability and runner tags are external moving parts. Parallel shard counts are manually tuned per device. Artifact dependencies must align with upload paths and architecture names. Lockdep failures are allowed, so master gating must inspect allowed-failure semantics. Device variable drift can submit invalid DTB or boot method combinations.

Test signals: pipeline expands expected per-driver jobs, LAVA submissions contain correct DUT variables and overlays, crosvm software jobs boot the kernel and run IGT, parallel shards divide test lists, xfail baselines are applied by driver/GPU version, and lockdep exit 101 is reported as allowed failure.

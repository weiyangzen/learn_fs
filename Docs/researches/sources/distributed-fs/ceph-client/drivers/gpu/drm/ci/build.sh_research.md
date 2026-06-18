# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build.sh

Purpose: builds DRM CI kernels for x86_64, arm64, and arm, packages kernel images, selected DTBs, modules, CI scripts, and configuration artifacts, and optionally uploads test-stage files to MinIO.

Important APIs/functions: after sourcing Mesa CI `container_pre_build.sh`, the script installs `libssl-dev` and `python3-lxml`, chooses `GCC_ARCH`, Debian arch, kernel image name behavior, and a curated DTB list based on `$KERNEL_ARCH`, exports `ARCH` and `CROSS_COMPILE`, creates `ld-links` symlinks to force BFD ld, configures Git identity, removes stale rebase directories, merges optional `*-external-fixes` branches from upstream/origin/MR target, creates `.config` via `merge_config.sh` or `make $(basename DEFCONFIG)`, applies `ENABLE_KCONFIGS` and `DISABLE_KCONFIGS` with `scripts/config`, builds kernel image(s), DTBs, modules, and module install tree, copies CI support files into `install`, sources `container_post_build.sh`, optionally uploads kernel files and `kernel-files.tar.zst`, then creates `artifacts/install.tar` plus `.config`.

Control flow: architecture branches define toolchain and DTB coverage. Upload branch is gated by `UPLOAD_TO_MINIO=1`. The script builds modules even for build-only jobs so test artifacts have loadable modules.

State and persistence: mutates git working tree by pulling external fixes, writes `.config`, kernel build outputs, `/kernel`, `install/`, `artifacts/`, and S3 objects. The final GitLab artifact is `artifacts/install.tar`, containing CI scripts, modules, images, and common test helpers.

Dependencies and integration points: depends on freedesktop/Mesa CI container helpers, Debian packages, kernel build system, cross compilers, GitLab variables (`UPSTREAM_REPO`, `TARGET_BRANCH`, MR vars), MinIO token variables, and `drivers/gpu/drm/ci/*` scripts. Feeds `testing:*`, LAVA, crosvm, dtbs, and KUnit jobs.

Risks: external-fixes pulls can change the tree under test and introduce merge failures. Device-tree lists are manually curated and can drift with kernel path renames. `apt-get` inside jobs adds mutable package dependencies. Some command substitutions use unquoted variables. Build failures may be obscured by large logs unless artifacts are preserved.

Test signals: artifact tar contains expected images/modules/scripts for each arch, DTBs exist for configured paths, external-fixes merge behavior on MR and non-MR pipelines, MinIO upload URLs, module install layout, and `.config` includes requested enable/disable fragments.

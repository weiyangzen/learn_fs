# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/build-igt.sh

Purpose: builds a pinned IGT GPU Tools tree inside the DRM CI container, installs it under `/igt`, generates a flattened CI test list including subtests, packages the result, and uploads it to MinIO/S3 for later test jobs.

Important APIs/functions: `generate_testlist()` reads IGT's `test-list.txt`, skips sentinel lines, runs each test binary with `--list-subtests`, and writes either plain test names or `test@subtest` entries to `/igt/libexec/igt-gpu-tools/ci-testlist.txt`. The main script clones `https://gitlab.freedesktop.org/drm/igt-gpu-tools.git`, checks out `$IGT_VERSION`, optionally creates an armhf Meson cross file for `KERNEL_ARCH=arm`, sets Meson options for disabled overlay/chamelium/valgrind and enabled tests/runner/man/libunwind, disables the xe driver on ARM/ARM64, builds with Ninja, installs to `/igt`, sets architecture-specific `LD_LIBRARY_PATH`, tars/gzips `/igt`, and uploads `igt.tar.gz` using `ci-fairy s3cp`.

Control flow: `set -ex` makes each command visible and aborts on failure except `--list-subtests`, where failures produce plain test entries. Ninja retries serially if the parallel build fails.

State and persistence: writes the clone, build directory, `/igt`, generated test list, `artifacts/igt.tar`, and uploaded S3 object at `${PIPELINE_ARTIFACTS_BASE}/${KERNEL_ARCH}/igt.tar.gz`.

Dependencies and integration points: depends on Git, Meson, Ninja, IGT build dependencies from the container image, optional Mesa CI cross-file helper, `FDO_CI_CONCURRENT`, `KERNEL_ARCH`, `IGT_VERSION`, `S3_JWT_FILE`, and `PIPELINE_ARTIFACTS_BASE`. Consumed by `igt_runner.sh` in LAVA/crosvm tests.

Risks: network clone and checkout are live external dependencies. `generate_testlist()` executes every IGT test binary in listing mode, so missing runtime libraries or broken binaries can silently collapse to whole-test entries. Upload path must match test runner architecture mapping. `tar -cf artifacts/igt.tar /igt` uses an absolute path and extraction later expects that layout.

Test signals: successful IGT checkout at the pinned SHA, Meson config for all three architectures, generated `ci-testlist.txt` containing subtests, S3 upload presence, and downstream runner extraction of `/igt`.

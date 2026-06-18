# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/kunit.sh

Purpose: runs DRM KUnit tests for the selected architecture using LLVM and the `drivers/gpu/drm/tests` KUnit configuration.

Important behavior: requires `KERNEL_ARCH` and `LLVM_VERSION`, runs `setup-llvm-links.sh`, prepends `/usr/bin` to `PATH`, then executes `./tools/testing/kunit/kunit.py run --arch "$KERNEL_ARCH" --make_options LLVM=1 --kunitconfig=drivers/gpu/drm/tests`.

Control flow: `set -euxo pipefail` aborts on missing variables or failed commands. Architecture-specific QEMU dependencies are installed by `kunit.yml`.

State and persistence: KUnit creates its normal build/test outputs under the kernel tree; no custom artifacts are written by this script.

Dependencies and integration points: depends on LLVM symlinks, kernel KUnit tooling, QEMU packages for target architecture, and the DRM tests KUnit config. Invoked by `kunit:*` GitLab jobs.

Risks: LLVM symlink setup writes to `/usr/bin`. KUnit architecture names must match KUnit's supported `--arch` values (`arm`, `arm64`, `x86_64`). Missing QEMU or incompatible kernel configs cause test boot failures rather than compile-only failures.

Test signals: KUnit compile and boot for all three architectures, `drivers/gpu/drm/tests` discovery, LLVM toolchain selection, and nonzero exit on failing KUnit assertions.

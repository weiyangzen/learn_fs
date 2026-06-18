# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/dtbs-check.sh

Purpose: runs architecture-specific `dtbs_check` under LLVM for DRM CI and reports schema warnings through a special allowed-failure exit code.

Important behavior: the script requires `KERNEL_ARCH` and `LLVM_VERSION`, calls `setup-llvm-links.sh`, runs `make LLVM=1 ARCH="$KERNEL_ARCH" defconfig`, then runs parallel `make ARCH="$KERNEL_ARCH" LLVM=1 dtbs_check DT_SCHEMA_FILES="${SCHEMA:-}"` with stderr redirected to `dtbs-check.log`. It exits 1 on make failure and 102 if the warning log is non-empty.

Control flow: setup is strict through `set -euxo pipefail` and parameter expansion guards. A clean `dtbs_check` with empty stderr exits 0.

State and persistence: writes `.config` and build artifacts through kernel make, plus `dtbs-check.log` for CI artifact collection.

Dependencies and integration points: depends on LLVM packages and symlinks, kernel DT build system, `dtschema` venv from the GitLab before_script, and the architecture variables supplied by `check-devicetrees.yml`.

Risks: `defconfig` is used rather than DRM CI's testing config, so check coverage follows architecture defaults. As with binding checks, any stderr output is treated as a warning. LLVM version symlink creation writes into `/usr/bin` and assumes job container privileges.

Test signals: arm32/arm64 execution, `setup-llvm-links.sh` success, warning-only exit 102, hard make failure exit 1, and schema filter honoring `SCHEMA`.

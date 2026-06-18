# sources/cloud-native/composefs-rs/examples/common/install-patched-tools

Purpose: builds patched/newer `systemd-repart` and `mkfs.ext4` into a caller-provided install path for fs-verity-capable image creation.

Important APIs/types/functions: clones `systemd` at `v258`, builds `systemd-repart`; clones `e2fsprogs` at `v1.47.3`, builds `mke2fs`, and copies it as `mkfs.ext4`.

Control flow: sequentially clones, checks out tags, configures/builds, creates install directories, and copies binaries/shared objects.

State/persistence: writes built tools under `$install_path` and leaves source/build trees in the current directory.

Dependencies/integration: depends on git, meson, ninja, configure/make, network access, and build dependencies.

Risks/test signals: destructive in current working directory if `systemd` or `e2fsprogs` already exist; pinned versions can age. `check-config` suggests this path when system tools lack fs-verity support.

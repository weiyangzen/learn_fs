<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/lib.sh -->
# sources/cloud-native/containers-storage/contrib/cirrus/lib.sh

- Purpose: Shared Cirrus shell library for environment normalization and dependency installation.
- Important functions: `bad_os_id_ver`, `lilto`, `bigto`, `install_fuse_overlayfs_from_git`, `install_bats_from_git`, and `check_filesystem_supported`.
- Control flow: Exports CI variables, sources containers automation common library when present, derives Go/source paths, computes `EPOCH_TEST_COMMIT`, defines package manager wrappers, and provides install/check helpers.
- State and persistence: Installs fuse-overlayfs and bats into system paths, clones temporary sources, and sets exported environment for child scripts.
- Dependencies and integration: Requires containers/automation helper functions, Go env, git, dnf/apt, sudo, and kernel module support checks.
- Risks: Heavy reliance on external automation library; global `set -a` export can leak variables; source installs from git are not version-pinned here.
- Test signals: Setup/build scripts successfully sourcing it and installing required tools.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/lib.sh -->

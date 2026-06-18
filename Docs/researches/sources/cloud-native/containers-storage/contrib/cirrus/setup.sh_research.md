<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/setup.sh -->
# sources/cloud-native/containers-storage/contrib/cirrus/setup.sh

- Purpose: Cirrus setup script that prepares Fedora/Debian test VMs.
- Important behavior: Sources `lib.sh`, shows environment, removes conflicting packages by distro, installs fuse-overlayfs from git, and installs bats.
- Control flow and state: Switches on `$OS_RELEASE_ID`; unsupported distributions call `bad_os_id_ver`.
- Dependencies and integration: Uses package wrappers and install helpers from `lib.sh`.
- Risks: Mutates host packages and installs from upstream git; unsupported distro detection must stay current with CI images.
- Test signals: Later build/test script finds fuse-overlayfs and bats.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/setup.sh -->

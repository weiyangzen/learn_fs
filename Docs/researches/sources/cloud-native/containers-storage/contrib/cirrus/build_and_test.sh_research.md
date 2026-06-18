<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/build_and_test.sh -->
# sources/cloud-native/containers-storage/contrib/cirrus/build_and_test.sh

- Purpose: Cirrus script that builds containers/storage and runs driver-specific test suites.
- Important behavior: Installs tools, runs local binary and cross builds, then switches on `TEST_DRIVER` for overlay, overlay-transient, fuse-overlay, fuse-overlay-whiteout, vfs, aufs, btrfs, and zfs variants.
- Control flow and state: Source `lib.sh`, cd to `$GOSRC`, run make targets with driver-specific environment, and for some drivers set up backing loop devices or skip unsupported filesystems.
- Dependencies and integration: Requires Cirrus environment, make targets, kernel/filesystem support, fuse-overlayfs, and automation helper functions like `showrun`.
- Risks: Driver tests are host-kernel sensitive; unsupported filesystems or missing modules must fail clearly.
- Test signals: Cirrus build/test task status for each matrix entry.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/build_and_test.sh -->

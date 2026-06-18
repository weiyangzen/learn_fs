<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/cmake.yml -->
# sources/cloud-native/overlaybd/.github/workflows/cmake.yml

Purpose: Main CI workflow for CMake builds, TCMU smoke coverage, raw image application, turboOCI v1 mounting, and unit tests on `ubuntu-22.04`.

APIs and control flow: On pushes and PRs to `main`, it installs system libraries, builds googletest, configures with `BUILD_TESTING=1`, `ENABLE_DSA=1`, and `ENABLE_ISAL=1`, then runs `make -j64`. E2E steps install OverlayBD, enable `overlaybd-tcmu.service`, create configfs TCMU devices, discover SCSI devices with `lsscsi`, mount read-only, and compare generated filesystem content.

State and persistence: It writes under `/etc/overlaybd`, `/opt/overlaybd`, `/var/lib/overlaybd/test`, `/sys/kernel/config/target`, local build dirs, and `/var/log/overlaybd.log`.

Dependencies and integration: Requires root-level configfs, target_core_user, libtcmu, libaio, curl, OpenSSL, ext2fs, zstd, json-c, kmod, systemd, gtest, and downloadable Azure blob test data.

Risks and test signals: High parallel build and kernel configfs assumptions make CI host-sensitive. Strong signals are successful mount, recursive diff, `overlaybd-apply` deterministic output, turboOCI mount, and `ctest`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/cmake.yml -->

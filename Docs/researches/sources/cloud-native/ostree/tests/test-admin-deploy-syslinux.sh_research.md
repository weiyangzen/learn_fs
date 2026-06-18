# sources/cloud-native/ostree/tests/test-admin-deploy-syslinux.sh

Purpose: runs shared admin deployment tests under syslinux and adds legacy boot-directory layout checks.

Important APIs/functions: `setup_os_repository "archive" "syslinux"`, `admin-test.sh`, `pull-local`, `ostree admin deploy`, and assertions for `boot/loader/entries`, `/boot/ostree`, and tree-local kernel/initramfs paths.

Control flow: executes the full `admin-test.sh` suite with three extra TAP cases, then iterates over legacy boot directories `boot` and `usr/lib/ostree-boot`, recreating the repository and verifying deployed boot assets are present in both sysroot boot storage and the deployment tree with checksummed names.

State/persistence: repeatedly recreates `sysroot`, `testos-repo`, and boot artifacts. Dependencies include syslinux fixture setup and `bootcsum`.

Integration/risk/test signals: covers syslinux-specific and historical boot path compatibility. Risks are exact path conventions and duplicate setup cost.

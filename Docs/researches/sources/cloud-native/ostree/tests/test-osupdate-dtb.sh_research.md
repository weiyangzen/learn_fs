<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-osupdate-dtb.sh -->
# sources/cloud-native/ostree/tests/test-osupdate-dtb.sh

## Purpose
`test-osupdate-dtb.sh` validates device-tree blob handling during OS updates and deployments.

## Important APIs, Types, And Functions
It uses `setup_os_repository "archive" "syslinux"`, creates DTB files under module directories including `dtb` and `dtb/overlays`, commits OS content, runs admin deploy/upgrade, and asserts files under `sysroot/boot/ostree`.

## Control Flow
The test deploys an initial tree without DTBs, verifies only the kernel is installed and no DTB files exist, then adds DTBs to a later tree and upgrades. It verifies boot directory generation changes from one to two boot checksums and that the expected number of `.dtb` files appears.

## State And Persistence
State is a temporary OS repo, sysroot, module directory content, boot checksum directories, kernel files, and DTB files.

## Dependencies And Integration Points
It covers admin deployment, boot artifact copying, syslinux layout behavior, and DTB discovery under kernel module paths.

## Risks And Test Signals
The test is sensitive to boot directory naming and DTB discovery rules. Passing signals include no stale DTBs for the first deployment and correct DTB propagation after upgrade.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-osupdate-dtb.sh -->

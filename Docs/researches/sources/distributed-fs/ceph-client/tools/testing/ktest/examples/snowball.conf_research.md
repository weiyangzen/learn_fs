# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/snowball.conf

## Purpose

This is an embedded ARM board example originally used for a Snowball board. It demonstrates non-x86 ktest usage with a cross-compile toolchain, TFTP-style image switching, script-based reboot, and a `make_min_config` workflow.

## Important APIs, Types, And Data

The config defines `THIS_DIR`, `LOG_FILE`, `MAKE_CMD` with ARM `CROSS_COMPILE` and `ARCH=arm`, `ADD_CONFIG`, `SCP_TO_TARGET` as a no-op echo, TFTP paths, `SWITCH_TO_GOOD`, `SWITCH_TO_TEST`, a skipped boot test, an active `TEST_TYPE=make_min_config` test, and a `DEFAULTS` block with `LOCALVERSION`, `POWER_CYCLE`, `CONSOLE`, `REBOOT_TYPE=script`, `SSH_USER`, `BUILD_OPTIONS=-j8 uImage`, `BUILD_DIR`, `OUTPUT_DIR`, `MACHINE`, `TARGET_IMAGE`, and `BUILD_TARGET=arch/arm/boot/uImage`.

## Control Flow

`ktest.pl` parses the skipped boot test but does not materialize it. The active test runs `make_min_config`, starting from `${THIS_DIR}/config.orig`, writing `${THIS_DIR}/config.newmin`, and tracking required configs in `${THIS_DIR}/config.ignore`. For booting, ktest uses `SWITCH_TO_TEST`/`SWITCH_TO_GOOD` copy commands instead of SCP, and `REBOOT_TYPE=script` leaves reboot behavior to configured script hooks.

## State And Persistence Behavior

Persistent state includes the Snowball build directory, TFTP boot images, generated minimum config files, and the ignored-required-config file. Because `SCP_TO_TARGET` is disabled, installation state is managed by copying build outputs to TFTP paths rather than transferring to the target filesystem.

## Dependencies And Integration Points

It depends on an ARM cross compiler under `/usr/local/gcc-4.5.2-nolibc/...`, TFTP paths under `/var/lib/tftpboot`, a console capture source `${THIS_DIR}/snowball-cat`, and ktest's script reboot/image switching hooks. It integrates with `make_min_config`, `ADD_CONFIG`, `BUILD_OPTIONS`, `BUILD_TARGET`, and `TARGET_IMAGE`.

## Risks And Edge Cases

Many paths are highly local to the original environment. `POWER_CYCLE` is an interactive placeholder, so unattended runs will pause. `SCP_TO_TARGET=echo` is intentional for TFTP but would silently skip normal target copies if copied to a different setup. The skipped boot test can be re-enabled accidentally by removing `SKIP` without completing power/reboot scripts.

## Test Signals

Dry-run should show one active `make_min_config` test, ARM make command, script reboot type, and TFTP target image paths. Runtime signals include creation of `config.newmin`/`config.ignore`, `uImage` builds in the Snowball output directory, and image copy commands to the TFTP boot path.

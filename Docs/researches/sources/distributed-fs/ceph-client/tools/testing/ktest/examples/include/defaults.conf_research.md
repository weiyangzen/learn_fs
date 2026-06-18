# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/defaults.conf

## Purpose

This include provides shared defaults for machine-specific ktest examples. It centralizes directory layout, SSH access, kernel build/install paths, reboot/power handling, logging, minimum config locations, and success-line defaults so individual machine configs can focus on target-specific console and test selection.

## Important APIs, Types, And Data

The file uses ktest `DEFAULTS IF NOT DEFINED`, unconditional `DEFAULTS`, and `DEFAULTS ELSE IF` blocks. Important variables/options include `BOX`, `BITS`, `THIS_DIR`, `CONFIG_DIR`, `CLEAR_LOG`, `SSH_USER`, `SSH`, `TEST`, `BUILD_DIR`, `OUTPUT_DIR`, `BUILD_TARGET`, `TARGET_IMAGE`, `SCRIPTS_DIR`, `POWER_CYCLE`, `POWER_OFF`, `LOCALVERSION`, `GRUB_MENU`, `BUILD_OPTIONS`, `LOG_FILE`, `MIN_CONFIG`, optional `ADD_CONFIG`, and `REBOOT_SUCCESS_LINE`. The `REBOOT` variable drives one of four policy branches: `none`, `error`, `fail`, or default.

## Control Flow

During config parsing, `ktest.pl` first defaults `BOX` to `${MACHINE}` and `BITS` to `64` if the including config did not set them. The main `DEFAULTS` block then sets common options. Conditional `DEFAULTS` branches translate the caller's `${REBOOT}` variable into `REBOOT_ON_SUCCESS`, `REBOOT_ON_ERROR`, `POWEROFF_ON_ERROR`, `POWEROFF_ON_SUCCESS`, `POWEROFF_AFTER_HALT`, `DIE_ON_FAILURE`, and `STORE_FAILURES`.

## State And Persistence Behavior

The include defines persistent output locations but does not write them itself. `ktest.pl` will create `${OUTPUT_DIR}`, write `${LOG_FILE}`, use `${CONFIG_DIR}/config-min`, and potentially write `${THIS_DIR}/failures` when failures occur. Power scripts under `${SCRIPTS_DIR}` and target bootloader entries are external persistent infrastructure.

## Dependencies And Integration Points

It depends on an including config setting at least `MACHINE` and a console, and on ktest's option map for all named options. It integrates with later includes (`patchcheck.conf`, `tests.conf`, `bisect.conf`, `min-config.conf`, `bootconfig.conf`) by defining common variables they reuse. It assumes x86 defaults for `BUILD_TARGET`, `TARGET_IMAGE`, and `GRUB_MENU`, while documenting that other architectures can override.

## Risks And Edge Cases

The default SSH user is `root` and assumes passwordless access, which is powerful and risky. `BUILD_DIR` and `OUTPUT_DIR` are under `${THIS_DIR}` and must not alias each other. The default `POWER_CYCLE`/`POWER_OFF` script names must exist for hardware tests. `REBOOT := empty` in examples falls into the default branch, enabling reboot on success and error. The `fail` policy disables `DIE_ON_FAILURE`, so failures may be logged while the run continues.

## Test Signals

`ktest.pl --dry-run` should resolve machine-specific `CONFIG_DIR`, `OUTPUT_DIR`, `LOG_FILE`, `MIN_CONFIG`, power commands, and reboot policy. Runtime validation includes log creation, build output under `${THIS_DIR}/build/${MACHINE}`, and correct reboot/power behavior for each `REBOOT` policy.

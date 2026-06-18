<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-base.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-base.c

## Purpose

This is the core I2C driver for the CZ.NIC Turris Omnia MCU. It provides shared I2C command helpers, reads firmware features and board identity, exposes base sysfs attributes, and registers optional MCU subfeatures.

## Important APIs, Types, And Functions

`omnia_cmd_write_read()` is the exported raw I2C transaction helper. `omnia_get_version_hash()` reads application or bootloader firmware hashes. Sysfs show functions expose firmware hashes, feature bitmap, MCU type, reset selector, serial number, first MAC, and board revision. `omnia_mcu_read_features()` reads status/features, determines MCU type, logs missing features, and handles 16-bit vs 32-bit feature responses. `omnia_mcu_read_board_info()` reads serial/MAC/revision. `omnia_mcu_probe()` initializes `struct omnia_mcu` and calls optional registration helpers.

## Control Flow

Probe requires an IRQ, allocates MCU state, reads features, optionally reads board info, then registers sys-off/wakeup, watchdog, GPIO chip, keyctl signing, and TRNG in sequence. The device's `dev_groups` include base attributes and optional feature groups, with visibility controlled by feature bits.

## State And Persistence

Persistent hardware information is cached in `mcu->features`, `mcu->type`, serial number, first MAC, and board revision. Firmware state remains in the MCU. Sysfs reads either cached identity data or live command responses.

## Dependencies And Integration Points

It depends on I2C, OF compatible `cznic,turris-omnia-mcu`, the public MCU command interface header, optional feature files, and sysfs device groups.

## Risks

Feature detection has compatibility logic for old firmware; mistakes can hide or expose unsupported features. Probe aborts on optional registration failure once a feature reports present. Board-info visibility depends on the feature bit, and board info read failures fail probe. I2C partial transfers return `-EIO`.

## Test Signals

Test probe with missing IRQ, old firmware without feature command, 16-bit and 32-bit feature reads, bootloader firmware warning, board info parsing, sysfs visibility, optional feature registration failures, and I2C error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-base.c -->

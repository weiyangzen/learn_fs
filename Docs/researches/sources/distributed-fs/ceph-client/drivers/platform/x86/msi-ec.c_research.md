<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.c

## Purpose
This MSI embedded controller driver selects an EC register map by firmware version and exposes battery charge start/end thresholds through the ACPI battery extension hook.

## Important APIs, Types, And Functions
Most of the file is a table of `struct msi_ec_conf` instances (`CONF0` through `CONF13`) with allowed firmware strings and EC addresses for charge control, webcam, function key swap, cooler boost, shift mode, fan mode, sensors, LEDs, and keyboard backlight. The active configuration is copied into global `conf`. `ec_read_seq()` and `ec_get_firmware_version()` read the universal firmware version bytes. `load_configuration()` matches firmware against `CONFIGS`. `charge_control_threshold_show/store()` implement offset-adjusted EC threshold reads/writes. `msi_battery_add/remove()` add or remove power-supply attributes.

## Control Flow
Module init reads EC firmware version at address `0xa0`, matches it against allowed firmware lists, and fails with `-EOPNOTSUPP` if unsupported. On success it registers a battery hook. When a battery power supply appears, the hook creates `charge_control_start_threshold` and `charge_control_end_threshold` files. Stores parse u8 percentages, add firmware-specific offsets, enforce configured raw ranges, and write the EC threshold register.

## State And Persistence
The selected `conf` is global module state. Threshold values are persisted in EC/firmware behavior, not in driver memory. The driver does not expose the many non-battery fields in the config table in this version.

## Dependencies And Integration Points
It depends on ACPI EC helpers `ec_read()`/`ec_write()`, ACPI battery hooks, DMI module metadata, and `msi-ec.h` configuration structs. Userspace integration is through power-supply sysfs battery threshold attributes.

## Risks And Edge Cases
The configuration table must exactly match firmware EC layouts; unsupported firmware is rejected to avoid writing wrong EC addresses. `MSI_EC_ADDR_UNKNOWN` and `MSI_EC_ADDR_UNSUPP` have the same sentinel value in the header, so table comments carry semantic nuance not represented programmatically. Only firmware version strings are used for selection.

## Test Signals
Tests should cover firmware string reads, each supported config match, unsupported/invalid firmware rejection, threshold show/store offset math, range checks, EC read/write failures, battery hook add/remove, and absence of attributes when init fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.c -->

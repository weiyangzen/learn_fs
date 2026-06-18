# sources/distributed-fs/ceph-client/drivers/acpi/ac.c

## Purpose
`ac.c` is the ACPI AC adapter power-supply driver for `ACPI0003` devices. It evaluates `_PSR` to expose whether mains power is online, reports ACPI/netlink notifier events, and registers a Linux power supply named after the ACPI device BID.

## Important APIs, Types, And Functions
The main state is `struct acpi_ac`, holding the `power_supply`, descriptor, ACPI device, cached state, and battery notifier. Important functions are `acpi_ac_get_state()`, `get_ac_property()`, `acpi_ac_notify()`, `acpi_ac_battery_notify()`, `thinkpad_e530_quirk()`, `ac_only_quirk()`, `acpi_ac_probe()`, `acpi_ac_resume()`, `acpi_ac_remove()`, `acpi_ac_init()`, and `acpi_ac_exit()`.

## Control Flow
Module init exits if ACPI is disabled or the platform quirk says to skip ACPI AC/battery, applies DMI quirks, and registers a platform driver. Probe fetches the ACPI companion, allocates `struct acpi_ac`, reads `_PSR` unless forced online by `ac_only`, registers a `POWER_SUPPLY_TYPE_MAINS` power supply with `POWER_SUPPLY_PROP_ONLINE`, subscribes to ACPI battery events, and installs an ACPI notify handler. Notify events optionally sleep for a DMI-configured EC delay, reread state, generate netlink and ACPI notifier-chain events, and call `power_supply_changed()`. Resume rereads state and emits a power-supply change if it differs.

## State And Persistence
State is in memory as the cached AC line state, DMI quirk flags, and registered power-supply object. User-visible state is exposed through power-supply sysfs and ACPI events. No durable persistence is used.

## Dependencies And Integration Points
It depends on ACPI platform enumeration, `_PSR`, Linux `power_supply`, DMI quirks, ACPI notifier chain, battery class events, and platform-driver PM operations. It uses `acpi_quirk_skip_acpi_ac_and_battery()` to respect broader platform quirks.

## Risks
Firmware notification ordering can make `_PSR` stale, hence the ThinkPad delay quirk. `ac_only` forces online state on systems with broken firmware, trading correctness for usability. Notification and battery callbacks both update cached state without a dedicated lock; consumers rely on simple scalar semantics. Probe error paths must keep notifier and power-supply registration ordering correct.

## Test Signals
Tests should cover `_PSR` online/offline/unknown results, ACPI notify events `0x80`, bus check, device check, resume transitions, battery-triggered rereads, DMI quirk behavior, and power-supply sysfs `online` updates.

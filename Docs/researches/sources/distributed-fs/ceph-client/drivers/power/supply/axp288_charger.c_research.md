<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp288_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp288_charger.c

## Purpose

`axp288_charger.c` is the native charger driver for the AXP288 PMIC used on Intel Bay Trail and Cherry Trail tablets. It exposes the charger as a USB power supply, manages constant charge current/voltage and input-current limits, reacts to charger-type and OTG extcon events, and applies hardware initialization and device-specific DMI quirks.

## Important APIs, Types, And Functions

`struct axp288_chrg_info` contains the parent regmap/IRQ controller, registered USB supply, mutex, charger and OTG extcon notifier state, current/voltage limits, cached input/op/backend registers, and a validity timestamp. `axp288_charger_set_cc()`, `axp288_charger_set_cv()`, `axp288_charger_set_vbus_inlmt()`, `axp288_charger_vbus_path_select()`, and `axp288_charger_enable_charger()` are the core register writers.

`axp288_charger_usb_update_property()` refreshes `AXP20X_PWR_INPUT_STATUS`, `AXP20X_PWR_OP_MODE`, and `AXP20X_CHRG_BAK_CTRL` with `iosf_mbi_block_punit_i2c_access()` held, then caches the result for 60 seconds. `axp288_charger_usb_get_property()` reports presence/online, health, current/voltage settings, and input-current limit. `axp288_charger_extcon_evt_worker()` maps SDP/CDP/DCP or HP Type-C DMI quirks to a current limit and enables charging.

## Control Flow

Probe first requires `acpi_quirk_skip_acpi_ac_and_battery()` so native drivers do not conflict with selected ACPI battery/AC drivers. It rejects devices where `AXP20X_CC_CTRL` is zero, allocates state, obtains the charger extcon `axp288_extcon`, optionally obtains an OTG host extcon (`INT3496:00` or `intel-int3496`), initializes charger hardware, registers the power supply, registers extcon work/notifiers, schedules initial cable and OTG processing, and requests all charger IRQs.

## State And Persistence

The driver caches charger register state and invalidates it on property writes, IRQs, and extcon changes. Hardware writes persist in AXP288 registers: temperature thresholds, charge-output behavior, termination current, OCV calibration disable, Vhold or HP vbus-path enable, charge CC/CV, charger enable, and VBUS input-current limit. `max_cc` and `max_cv` are initialized from firmware-provided register values and cap later user writes.

## Dependencies And Integration Points

Dependencies include the AXP20x MFD/regmap IRQ core, Intel IOSF MBI arbitration, x86 ACPI quirks, extcon charger-type provider `axp288_extcon`, optional USB-host extcon, DMI matching for HP Pavilion x2 Type-C variants, and the power-supply framework.

## Risks And Edge Cases

The driver intentionally uses native mode only on systems opted out of ACPI AC/battery. Incorrect ACPI quirk detection can cause duplicate or missing power supplies. Extcon charger-type detection can be in progress; the worker returns without changing limits until a type is known. OTG host mode forces reported present/online to false and disables VBUS path, so extcon ID errors can block charging. Cached state can be stale for up to 60 seconds unless invalidated. HP Type-C DMI behavior hardcodes 3 A and enables VBUS path at probe.

## Test Signals

Test charger registration on supported AXP288 systems, rejection when ACPI drivers should own the device, SDP/CDP/DCP current-limit mapping, HP Pavilion x2 Type-C behavior, OTG host attach/detach VBUS path control, all nine charger IRQs, P-unit I2C blocking/unblocking on error paths, and sysfs writes for CC, CV, and input-current limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp288_charger.c -->

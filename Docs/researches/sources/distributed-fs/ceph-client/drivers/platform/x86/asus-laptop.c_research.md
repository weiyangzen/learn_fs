# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-laptop.c

## Purpose
`asus-laptop.c` is the legacy ACPI ATKD ASUS laptop support driver. It exposes hotkey events, vendor backlight, LED controls, wireless/GPS rfkill, ambient-light controls, display switching, and Pegatron Lucid tablet extras for systems using ACPI IDs `ATK0100` and `ATK0101`.

## Important APIs, Types, and Functions
`struct asus_laptop` is the central per-device state: ACPI device/handle, platform device, backlight, input devices, LED descriptors, rfkill descriptors, cached wireless/light/LEDD state, model name, DSDT header, and event counters. `struct asus_led` wraps LED class devices and work items. `struct asus_rfkill` wraps rfkill devices and control IDs. ACPI helpers `write_acpi_int_ret()`, `write_acpi_int()`, and `acpi_check_handle()` are used throughout.

Major subsystems are initialized by `asus_platform_init()`, `asus_backlight_init()`, `asus_input_init()`, `asus_led_init()`, `asus_rfkill_init()`, `pega_accel_init()`, and `pega_rfkill_init()`. Sysfs handlers expose `infos`, `wlan`, `bluetooth`, `wimax`, `wwan`, `display`, `ledd`, `ls_value`, `ls_level`, `ls_switch`, and `gps`. ACPI notifications are handled by `asus_acpi_notify()`.

## Control Flow
Module init registers a base platform driver and the ACPI platform driver, then requires that at least one ACPI device probe succeeded. Probe allocates `struct asus_laptop`, sets ACPI name/class, applies DMI adjustments, initializes ACPI state by calling `INIT`, `BSTS`, and `CWAP`, detects RSTS support, detects Pegatron Lucid features, creates the platform device/sysfs group, conditionally registers vendor backlight when ACPI video policy selects vendor backlight, then registers input, LEDs, rfkill, Pegatron accelerometer/rfkill, and ACPI notify handler.

Runtime ACPI notifications generate netlink events with per-event counters, normalize brightness ranges to a single up/down event, update backlight state for brightness events, emit accelerometer uevents for Pegatron orientation changes, or report sparse-keymap input events. Sysfs writes generally parse integers and call corresponding ACPI methods. LED writes are deferred to a single-thread workqueue to avoid ACPI calls in unsafe contexts. Remove unwinds notify, backlight, rfkill, LED, input, accelerometer, platform device, and allocations.

## State and Persistence
The driver caches mutable state in `struct asus_laptop`: `ledd_status`, `light_level`, `light_switch`, wireless status fallback bits, Pegatron accelerometer readings, event counters, and module-parameter-derived initial settings. Actual hardware state is controlled through ACPI methods such as `WLED`, `BLED`, `GSMC`, `WMXC`, `SPLV`, `SDSP`, `ALSC`, `ALSL`, `SDON`, and `SDOF`. Module parameters set boot-time behavior but are not runtime persistent.

## Dependencies and Integration Points
The file integrates with ACPI platform-device matching, ACPI video backlight policy, input sparse keymaps, LED class devices, backlight core, rfkill, platform sysfs, DMI, and ACPI netlink events. It is separate from newer ASUS WMI drivers and covers older ATKD firmware interfaces.

## Risks and Test Signals
Risks include fragile ACPI firmware behavior, many optional methods, and legacy raw assumptions. `asus_sysfs_is_visible()` guards sysfs files by probing ACPI methods, which is important because many models expose only a subset. LED unregister is called for all LED structs even if not registered, matching common classdev tolerance but still worth testing. `asus_laptop_get_info()` allocates the ACPI output buffer and model string; allocation and cleanup paths are important. Test signals include successful probe on ATK0100/ATK0101 only, no device causing module init failure, sysfs visibility per ACPI method, brightness event handling with and without vendor backlight, rfkill setup for WLAN/Bluetooth/WWAN/WiMAX/GPS, Pegatron accelerometer polling and fake first report, ACPI notify input mapping, and orderly cleanup on each probe failure label.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/loongson-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/loongarch/loongson-laptop.c

## Purpose

This ACPI driver supports Loongson laptops and all-in-one systems. It registers a hotkey input device from firmware keymap data, handles ACPI notifications, manages vendor backlight control, and reports lid/switch events.

## Important APIs, Types, And Functions

`struct generic_sub_driver` abstracts ACPI subdrivers. Global state includes `generic_inputdev`, `hotkey_handle`, `hotkey_keycode_map`, and `bl_powered`. `acpi_evalf()` is a local ACPI method helper. Hotkey setup uses `hotkey_map()`, `sparse_keymap_setup()`, and `event_notify()`. Backlight functions call ACPI methods `ECBG`, `ECBS`, `ECLL`, `ECSL`, `VCBL`, and `\BLSW`. `generic_acpi_laptop_init()` is the module entry point.

## Control Flow

Module init requires ACPI and an EC HID `PNP0C09`, enables SCI, allocates an input device, registers the hotkey platform subdriver for `LOON0000`, parses the `KMAP` ACPI package, installs an ACPI notify handler, registers the input device, and optionally registers a platform backlight if brightness methods exist. ACPI notifications are decoded into event type and scan code, looked up in the sparse keymap, and reported. Resume refreshes backlight state and may report lid state if firmware supports `SW_LID`.

## State And Persistence

Most state is global singleton state: the input device, hotkey ACPI handle, keymap, registered flag, and backlight power flag. Firmware owns brightness and hotkey status. No settings are persisted by the driver beyond ACPI method effects.

## Dependencies And Integration Points

It depends on ACPI, ACPI EC, ACPI video backlight policy, input sparse keymap, backlight class, platform driver core, and Loongson-specific ACPI methods/HIDs.

## Risks

`hotkey_map()` does not visibly free the ACPI allocated buffer and does not clamp package count to `GENERIC_HOTKEY_MAP_MAX`, making malformed firmware a risk. `backlight_device_register()` return value is ignored, and no unregister path stores the pointer. The driver uses global singleton state, so multiple matching devices are not supported. ACPI helper format handling is minimal.

## Test Signals

Test systems with and without `PNP0C09`/`LOON0000`, valid and oversized `KMAP`, hotkey and lid notifications, vendor vs non-vendor backlight policy, brightness get/set bounds, suspend/resume lid/backlight handling, module unload, and ACPI method failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/loongson-laptop.c -->

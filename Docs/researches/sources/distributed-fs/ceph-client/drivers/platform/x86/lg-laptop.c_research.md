<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lg-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lg-laptop.c

## Purpose
This LG Gram platform driver exposes LG ACPI/WMI hotkeys, platform controls, battery charge limiting, LEDs, keyboard backlight, and an LG-specific ACPI operation-region handler.

## Important APIs, Types, And Functions
The driver uses WMI event GUIDs for hotkeys and ACPI methods `WMAB`, `WMBB`, and `\_SB.GGOV`. `lg_wmab()` and `lg_wmbb()` wrap firmware calls. Sysfs attributes include `fan_mode`, `usb_charge`, `reader_mode`, `fn_lock`, `charge_control_end_threshold`, and legacy `battery_care_limit`. LED class devices are `kbd_backlight` and `tpad_led`. `wmi_input_setup()` registers sparse hotkeys and WMI notify handlers. `lg_laptop_address_space_handler()` services LG address space `0x8F`. `acpi_probe()` installs the handler, creates a platform device, registers sysfs/LED/input/battery hooks, and selects WMBB battery-limit path based on DMI-derived year.

## Control Flow
ACPI platform probe for `LGEX0820` installs an opregion handler, registers a child platform device, creates attributes, registers optional LEDs, sets up WMI input handlers, and registers a battery hook. WMI notify maps known event codes to sparse key events or hardware-changed keyboard-backlight notification. Sysfs show/store methods perform firmware get/set calls and validate return object types.

## State And Persistence
Global state includes the platform device pointer, WMI input device, initialization bitmask, battery-limit method selection, and LED classdevs. Feature values live in firmware/EC. The address-space handler does not persist values; it logs or returns debug flags.

## Dependencies And Integration Points
Dependencies include ACPI platform matching, WMI legacy notify handlers, input sparse-keymap, LED class, ACPI battery hooks, DMI product parsing, and the LG firmware methods. Battery threshold is exposed both on the platform device and battery power-supply device.

## Risks And Edge Cases
The code uses global singleton state and legacy WMI APIs. WMBB buffer layout relies on fixed offsets such as `0x10`. DMI year parsing is heuristic and controls battery-limit method selection. LED registration failures are ignored as optional. Unknown opregion writes are ratelimited and ignored to keep firmware running.

## Test Signals
Tests should exercise all sysfs attributes, WMAB/WMBB object type validation, keyboard backlight hardware-change notifications, battery hook file creation/removal, opregion read/write callbacks with `fw_debug`, DMI model-year parsing, and clean unload after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lg-laptop.c -->

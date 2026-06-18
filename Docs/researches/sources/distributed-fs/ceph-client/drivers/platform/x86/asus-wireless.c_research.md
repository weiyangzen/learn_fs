# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wireless.c

## Purpose
`asus-wireless.c` is a small ACPI platform driver for Asus wireless radio control devices with ACPI IDs `ATK4001` and `ATK4002`. It exposes the airplane/radio hotkey as an input event and, where supported, exposes the firmware radio LED through the LED class.

## Important APIs, Types, And Functions
`struct hswc_params` describes the firmware-specific values passed to the `HSWC` ACPI method for on, off, and status operations. `struct asus_wireless_data` stores the ACPI companion, input device, LED class device, single-thread workqueue, pending LED state, and selected HSWC parameters.

`asus_wireless_method()` wraps `acpi_evaluate_integer()` with a single integer parameter. `led_state_get()`, `led_state_set()`, and `led_state_update()` implement the LED class callbacks and defer writes to the workqueue. `asus_wireless_notify()` handles ACPI notify event `0x88` by emitting a press/release pair for `KEY_RFKILL`.

## Control Flow
Probe allocates driver data, registers an input device named `Asus Wireless Radio Control`, and sets it up for `KEY_RFKILL`. It then matches the ACPI ID to HSWC parameter data. If parameters exist, it creates a workqueue, initializes the airplane LED, registers the LED class device, and installs an ACPI device notify handler. Remove unregisters the notify handler, LED class device, and workqueue.

## State And Persistence
The only mutable state is `led_state`, a queued firmware command value. The actual radio/LED state lives in firmware and is read with `HSWC status`. There is no persistent kernel configuration and no sysfs-specific state beyond the LED class device.

## Dependencies And Integration Points
The driver integrates with ACPI platform devices, the Linux input subsystem, LED class, and default rfkill LED triggers. It intentionally overlaps with Asus WMI radio handling but targets the ASHS/ATK400x ACPI device path, and `asus-wmi.c` checks for these IDs to avoid conflicting rfkill ownership in some cases.

## Risks
Only ACPI event `0x88` is understood; other events are logged as unknown. LED writes are asynchronous, so rapid userspace writes collapse to the last queued `led_state`. Probe registers the input device before HSWC parameter matching, meaning unmatched variants still get hotkey reporting but no LED control.

## Test Signals
Test by loading on ATK4001 and ATK4002 systems, confirming `KEY_RFKILL` events on firmware notification `0x88`, validating LED brightness get/set maps to the right HSWC values for both ID variants, checking suspend/resume LED behavior through `LED_CORE_SUSPENDRESUME`, and verifying remove cancels firmware notification delivery and destroys the workqueue cleanly.

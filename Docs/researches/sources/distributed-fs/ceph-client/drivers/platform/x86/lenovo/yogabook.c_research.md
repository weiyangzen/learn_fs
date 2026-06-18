<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yogabook.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yogabook.c

## Purpose
This driver manages Lenovo Yoga Book YB1 keyboard-half mode switching. The device can expose either a capacitive touch keyboard or a Wacom digitizer, but not both at once; the driver switches child device driver binding, pen LED, and keyboard backlight based on hall sensor and mode button events.

## Important APIs, Types, And Functions
`struct yogabook_data` holds ACPI/I2C device references, GPIOs, IRQs, PWM, LED devices, work item, flags, and backlight callback. `yogabook_work()` is the central state machine. `yogabook_toggle_digitizer_mode()` flips digitizer mode and schedules work. Shared probe/remove/suspend/resume logic is in `yogabook_probe()`, `yogabook_remove()`, `yogabook_suspend()`, and `yogabook_resume()`. The WMI path uses `KBLC()` on the Goodix ACPI device; the platform path uses PWM and GPIO.

## Control Flow
The module registers both WMI and platform drivers. WMI targets Windows Yoga Book models through button WMI GUID `243FEC1D-1963-41C1-8100-06A9D82A94B4`; platform probe targets Android models by device names and GPIO/PWM lookups. The work function disables currently active devices before enabling the selected one, using `device_release_driver()` and `device_reprobe()`. Tablet mode disables both keyboard and digitizer.

## State And Persistence
Flags track keyboard on, digitizer on, digitizer mode, tablet mode, and suspended state. Brightness is cached in `data->brightness`. Device binding state is manipulated at runtime and restored on remove if either child was released.

## Dependencies And Integration Points
The driver integrates ACPI device lookup, WMI events, I2C device lookup, GPIO lookup tables, PWM, LED class devices, IRQs, workqueues, and PM callbacks. It also uses a lookup for the pen indicator LED provider.

## Risks And Edge Cases
The driver deliberately unbinds/reprobes other drivers, so ordering with Goodix and Wacom probes matters and can defer. Work is scheduled to avoid ACPI deadlocks from event context. Suspend suppresses switching and turns off keyboard backlight if needed. Removal must reprobe released child devices, and failures are only warned.

## Test Signals
Tests should cover WMI and platform variants, mode button toggles, backside hall IRQ tablet transitions, pen touch IRQ on Android models, backlight LED brightness persistence, suspend/resume with pending work, child driver reprobe failures, and cleanup of ACPI/device references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yogabook.c -->

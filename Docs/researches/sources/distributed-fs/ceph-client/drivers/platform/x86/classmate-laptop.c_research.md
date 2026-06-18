# sources/distributed-fs/ceph-client/drivers/platform/x86/classmate-laptop.c

## Purpose
`classmate-laptop.c` supports Intel Classmate PC ACPI devices. It registers separate ACPI drivers for accelerometers, tablet-mode switch, backlight/rfkill control, and extra hotkeys, translating model-specific ACPI methods and notifications into standard Linux input, backlight, and rfkill interfaces.

## Important APIs, Types, And Functions
`struct cmpc_accel` stores accelerometer sensitivity, g-select, and open/closed state for v4 devices. `cmpc_add_acpi_notify_device()` and `cmpc_remove_acpi_notify_device()` are shared helpers for ACPI-notify-backed input devices.

There are two accelerometer implementations: v4 (`ACCE0001`) uses four-argument `ACMD` calls, signed 16-bit XYZ data, sensitivity and `g_select` sysfs attributes, and PM suspend/resume restart logic; pre-v4 (`ACCE0000`) uses two-argument `ACMD` calls, unsigned byte XYZ data, and a sensitivity attribute. Tablet mode (`TBLT0000`) uses `TCMD`. Backlight and WLAN rfkill (`IPML200`) use `GRDI`/`GWRI` commands for brightness selector `0xC0` and WLAN selector `0xC1`. Extra keys (`FNBT0000`) map low event nibbles to Linux key codes and use bit `0x10` as release state.

## Control Flow
Module init registers ACPI drivers in order: keys, IPML/backlight/rfkill, tablet, old accelerometer, and v4 accelerometer. On failure it unregisters previously registered drivers in reverse order. Exit unregisters all drivers.

Accelerometer add allocates state, writes default sensitivity and optionally g-select, creates sysfs attributes, then registers an input device. Opening the input device starts firmware reporting, notifications with event `0x81` read XYZ data and report ABS axes, and close stops reporting. V4 suspend stops the sensor only if it was open and resume reapplies settings and restarts it.

Tablet add registers an input switch device and initializes `SW_TABLET_MODE`; notification `0x81` refreshes state. IPML add registers a platform backlight and rfkill device against the same ACPI handle. Keys add registers an input device and reports key press/release from ACPI notify events.

## State And Persistence
Accelerometer sensitivity and g-select are kernel-side cached values mirrored into firmware when changed and when the v4 input device opens/resumes. V4 open state is tracked so suspend/resume only restarts active sensors. Backlight brightness and WLAN rfkill state live in ACPI firmware. Input devices and ACPI driver registrations are runtime-only.

## Dependencies And Integration Points
The driver depends on ACPI bus drivers and notifications, Linux input, backlight, rfkill, sysfs attributes, PM sleep ops, and standard module init/exit. It exposes multiple ACPI HIDs in one module through separate `struct acpi_driver` instances.

## Risks
Several ACPI buffer paths trust firmware object types and buffer lengths, especially accelerometer reads. Older accelerometer sensitivity has no explicit range check, while v4 validates sensitivity and g-select. `cmpc_ipml_add()` treats any non-NULL rfkill allocation as registerable, so error-pointer behavior relies on rfkill API conventions. Removal of accelerometer devices unregisters input devices but the allocated `cmpc_accel` state is not explicitly freed on normal remove in the visible code, which is a leak risk unless handled by surrounding kernel allocation semantics in this tree.

## Test Signals
Test registration/unregistration ordering, ACPI HID matching, accelerometer open/close and event `0x81` reports for old and v4 devices, v4 sysfs sensitivity/g-select validation and resume restart, tablet switch initial and notify state, backlight brightness get/set, WLAN rfkill query/block behavior, extra key press/release mapping including NL3 WLAN events, and init failure unwind at each ACPI driver registration step.

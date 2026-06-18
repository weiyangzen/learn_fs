# sources/distributed-fs/ceph-client/drivers/platform/x86/bitland-mifs-wmi.c

## Purpose
`bitland-mifs-wmi.c` is a WMI driver for Bitland notebooks implementing the MIFS/MiInterface protocol. It exposes system performance profile, fan and temperature monitoring, keyboard backlight brightness, GPU and keyboard RGB modes, fan boost, and selected hotkeys/events.

## Important APIs, Types, And Functions
The protocol uses packed `struct bitland_mifs_input`, `struct bitland_mifs_output`, and `struct bitland_mifs_event`. `bitland_mifs_wmi_call()` serializes WMI calls with a mutex and invokes either a procedure for SET operations without output or a method for GET operations with output.

`struct bitland_mifs_wmi_data` stores the WMI device, lock, keyboard LED, notifier block, input device, hwmon device, platform-profile device, and saved profile. The driver handles two WMI GUIDs: a control GUID for feature calls and an event GUID for notifications. A blocking notifier chain bridges event-device notifications to the control-device LED, hwmon, and platform-profile registrations.

Subsystem callbacks include `laptop_profile_get()/set()`, `laptop_hwmon_read()`, `laptop_kbd_led_set()/get()`, sysfs handlers for `gpu_mode`, `kb_mode`, and `fan_boost`, and `bitland_mifs_wmi_notify()` for event dispatch.

## Control Flow
Probe allocates state and initializes the WMI-call mutex. For the event GUID, it registers an input device using a sparse keymap for app/calculator/browser hotkeys. For the control GUID, it registers platform profile choices, an hwmon device, a keyboard backlight LED, and a notifier callback.

Profile set maps Linux platform profiles to firmware modes. Balanced-performance and performance first call `bitland_check_performance_capability()`, which requires system AC power and the circular-hole AC type rather than USB-C. Suspend saves the current profile and resume restores it.

Notifications validate event type, then update keyboard brightness, notify platform-profile changes, report sparse-keymap hotkeys, notify hwmon fan channels for CPU/GPU fan events, or log informational state changes.

## State And Persistence
The firmware stores all actual device state. The kernel caches only `saved_profile` for suspend/resume and registration objects. The blocking notifier chain is process-wide within the driver and allows the event WMI device instance to notify the control instance even though `no_singleton = true` permits both GUID-backed devices.

## Dependencies And Integration Points
The driver integrates with WMI device APIs, platform profile, power supply system-supplied checks, hwmon, LED class, input sparse keymaps, sysfs device groups, PM sleep ops, unaligned little-endian helpers, and a blocking notifier chain.

## Risks
The notifier chain assumes event and control devices coexist; events arriving before the control side registers will not update LED/hwmon/profile state. Performance profile writes are power-source gated and may fail when running on battery or USB-C. `bitland_mifs_wmi_call()` trusts output buffer sizing from `wmidev_invoke_method()` and copies the fixed output struct. Event hotkey reporting takes the WMI-call mutex even though it does not call WMI, which serializes against control calls but may be unnecessary.

## Test Signals
Test both WMI GUID instances, platform-profile get/set including AC-type rejection, suspend/resume profile restoration, hwmon CPU temp and three fan reads, keyboard LED get/set and hardware-change notification, sysfs `gpu_mode`, `kb_mode`, `fan_boost`, sparse key events for open-app/calculator/browser, fan event notifications to hwmon, and removal of notifier callbacks through devm cleanup.

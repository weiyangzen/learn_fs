# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-acpi.c

Purpose: main Uniwill notebook extras driver. It exposes EC-backed sysfs controls, hwmon sensors, multicolor lightbar LED control, battery health/charge-threshold extensions, hotkey input, and suspend/resume restoration for selected Uniwill/TUXEDO/Schenker/Intel systems.

Important APIs and types: `struct uniwill_data` owns the ACPI handle, EC regmap, feature bitmap, battery hook/list, locks, LED class device, input device, WMI notifier, and cached restore state. `struct uniwill_device_descriptor` supplies DMI-selected feature flags and optional probe callbacks. The regmap bus maps `ECRR`/`ECRW` ACPI methods to 16-bit EC registers with 8-bit values. Sysfs attributes include `fn_lock`, `super_key_enable`, `touchpad_toggle_enable`, `rainbow_animation`, `breathing_in_suspend`, `ctgp_offset`, and `usb_c_power_priority`.

Control flow: module init DMI-matches a descriptor unless `force` is set, registers the platform driver, then manually registers the Uniwill WMI event driver. Platform probe initializes regmap, enables EC manual control, applies descriptor/probe-derived features, then initializes battery hooks, lightbar, hwmon, NVIDIA CTGP, USB-C priority, and input/WMI notifications. Notifier events refresh batteries, restore USB-C power priority on AC changes, notify fn-lock sysfs, or report sparse-keymap input events.

State and persistence: EC state is modified in hardware and partially cached in regmap. Driver state caches charge control, fn-lock, super-key, and USB-C priority for suspend/resume. Manual EC control is cleared by devm action and shutdown. Battery list membership is protected by `battery_lock`; super key, LED writes, input reports, and USB-C priority have dedicated locks.

Dependencies and integration: depends on ACPI methods `ECRR`/`ECRW`, DMI descriptors, regmap, hwmon, LED multicolor, power-supply extension APIs, ACPI battery hooks, input sparse-keymap, and `uniwill-wmi.c` notifier delivery.

Risks and test signals: EC register semantics are model-specific, so DMI feature descriptors are safety-critical. Suspend/resume restore paths must not desynchronize volatile registers. Tests should verify each visible sysfs attribute only appears for supported features, EC manual control is cleared on removal/shutdown, hwmon values scale correctly, LED AC/battery registers stay in sync, battery extensions unregister cleanly, WMI events produce expected input/sysfs/power-supply updates, and DMI-gated probe rejects unsupported systems unless forced.

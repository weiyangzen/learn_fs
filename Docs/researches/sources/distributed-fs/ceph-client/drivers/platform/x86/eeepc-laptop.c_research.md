## sources/distributed-fs/ceph-client/drivers/platform/x86/eeepc-laptop.c

Purpose: legacy ASUS Eee PC ACPI extras driver for HID `ASUS010`. It exposes hotkeys, vendor backlight, sysfs control methods, hwmon fan controls, touchpad LED, rfkill devices, and optional WLAN PCI hotplug.

Important APIs/types/functions: `struct eeepc_laptop` stores ACPI handle, supported control-method bitmask, platform/backlight/input/rfkill objects, hotplug slot, LED workqueue, and event counters. `get_acpi()`/`set_acpi()` call model-specific ACPI methods from `cm_getv`/`cm_setv`. Sysfs helpers expose camera, card reader, display switch, CPU frequency control, and cpufv disabled state. EC fan helpers read/write fan PWM/RPM/control registers. Backlight ops read/write `PBLG/PBLS`. Input uses `eeepc_keymap`. Rfkill setup creates WLAN/Bluetooth/WWAN/WiMAX rfkill devices and can rescan/remove PCI WLAN devices.

Control flow: module registers a generic platform PM driver and the ACPI platform driver. Probe allocates state, applies DMI quirks, calls `INIT` and `CMSG`, creates the fixed `eeepc` platform device, optionally registers vendor backlight, input, hwmon, LED, rfkill/hotplug, and ACPI notify handler. Notify sends netlink events, handles brightness specially, and reports sparse keymap events.

State and persistence: ACPI control methods change firmware device state. Driver state includes event counters, rfkill state, cpufv/hotplug DMI flags, LED workqueue state, and platform sysfs exposure. Resume restores rfkill/hotplug and LED-related WLAN state.

Dependencies and integration: ACPI video, ACPI EC, input sparse-keymap, backlight, hwmon, rfkill, PCI hotplug, DMI, LED class, platform device/driver APIs.

Risks: broad hardware control in one driver creates complex unwind ordering. WLAN hotplug has DMI blacklists due to model-specific breakage. Direct EC fan access lacks detailed error handling. Test signals include probe on ASUS010 systems, DMI quirk paths, brightness notifications with/without ACPI video, sysfs controls, rfkill toggles, PCI hotplug consistency checks, fan hwmon values, suspend/thaw/restore, and module unload ordering.

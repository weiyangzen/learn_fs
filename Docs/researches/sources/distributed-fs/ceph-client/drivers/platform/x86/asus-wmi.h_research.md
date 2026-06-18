# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.h

## Purpose
`asus-wmi.h` is the local private interface between the generic Asus WMI core and model-specific platform drivers in the same driver family. It defines quirk flags, key-filter hooks, and the `asus_wmi_driver` registration contract implemented by `asus-wmi.c`.

## Important APIs, Types, And Functions
`enum asus_wmi_tablet_switch_mode` identifies which WMI device/event pair should be used for tablet mode reporting. `struct quirk_entry` holds model behavior switches such as wireless hotplug support, scalar brightness, stored backlight power, forced ALS enabling, ignored fan support, i8042 filtering, display-toggle suppression, WAPF behavior, and USB port remapping.

`struct asus_wmi_driver` is the main model-driver descriptor. It carries mutable cached fields for brightness/panel/screenpad/wireless ownership, static identity strings, the event GUID, sparse keymap, input naming, quirk pointer, optional WMI key filter, optional i8042 filter, optional model probe and quirk detection callbacks, and the embedded `platform_driver`/`platform_device` used by the core. The exported functions are `asus_wmi_register_driver()` and `asus_wmi_unregister_driver()`.

## Control Flow
Model drivers populate `struct asus_wmi_driver` and call `asus_wmi_register_driver()`. The core fills in platform driver callbacks, creates the platform bundle, and later calls the model callbacks during probe. On unload, the model calls `asus_wmi_unregister_driver()` to unregister the platform device/driver pair.

## State And Persistence
The header itself stores no state, but its structures define which state is shared between model frontends and the core. `quirk_entry` is effectively static policy. The mutable fields in `asus_wmi_driver` are runtime caches used by backlight, screenpad, and wireless-control logic.

## Dependencies And Integration Points
It depends on `linux/platform_device.h` and `linux/i8042.h`, plus forward declarations of `struct module`, `struct key_entry`, and `struct asus_wmi`. It is included by the Asus WMI core and sibling model drivers, while public WMI device IDs come from `<linux/platform_data/x86/asus-wmi.h>`.

## Risks
Because the core mutates fields inside the model-provided `asus_wmi_driver`, callers must treat the descriptor as live driver state, not read-only metadata. Quirk defaults are security- and hardware-sensitive: a wrong display-toggle, fan, backlight, or hotplug quirk can suppress real events or write unsafe firmware state. Only one Asus WMI driver can be registered at a time in the core.

## Test Signals
Compile coverage should catch structure drift between model drivers and the core. Runtime signals include successful model-driver registration/unregistration, quirk detection being visible in `asus_wmi_add()`, key-filter behavior changing event reporting, and i8042 filters installing only for models that request them.

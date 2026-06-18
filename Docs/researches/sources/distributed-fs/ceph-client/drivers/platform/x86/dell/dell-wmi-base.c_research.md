## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-base.c

Purpose: main Dell WMI hotkey/event driver for laptop-class systems using event GUID `9DBB5994-A997-11DA-B012-B622A1EF5492`. It translates WMI event buffers into input events, tablet switch events, privacy events, and Dell laptop notifier callbacks.

Important APIs, types, and functions: `struct dell_wmi_priv` stores the main input device, optional tablet switch device, and descriptor interface version. Static keymaps cover WMI event types `0x0000`, `0x0010`, `0x0011`, and `0x0012`; DMI type `0xB2` hotkey tables can augment type `0x0010`. `handle_dmi_entry()` builds a runtime sparse keymap from BIOS keycodes. `dell_wmi_process_key()` handles brightness suppression when ACPI video owns brightness keys, keyboard illumination notification, tablet-mode switch reporting, ePrivacy key selection, and ultra-performance value handling. `dell_wmi_notify()` parses one or more length-prefixed u16 events and delegates to privacy handling first for eligible type `0x0012` events. `dell_wmi_events_set_enabled()` uses Dell SMBIOS application registration on specific DMI systems.

Control flow: late init checks DMI quirks, optionally enables WMI events through SMBIOS, registers the Dell privacy subdriver, then registers a WMI driver. Probe gates on `dell_wmi_get_descriptor_valid()` and descriptor interface version, then creates sparse-keymap input. Notify parses buffers differently for descriptor interface version 0 to avoid stale trailing data.

State and persistence: runtime input devices and tablet switch device live per WMI device. `wmi_requires_smbios_request` is a module-global DMI quirk. Firmware event registration is enabled at init and disabled at exit for affected systems.

Dependencies and integration: depends on `dell-wmi-descriptor`, `dell-smbios`, `dell-laptop` notifier, `dell-wmi-privacy`, ACPI video, WMI, input, and sparse-keymap.

Risks: event parsing depends on firmware-provided lengths and the version-specific stale-buffer workaround. Keymap merging has duplicate-suppression only for DMI-derived type `0x0010` entries. Privacy and hotkey handling share type `0x0012`, so ordering matters. Test signals include descriptor probe ordering, DMI hotkey-table systems, type 0/1 multi-event buffers, privacy events, tablet-mode event `0xe070`, brightness-key suppression under ACPI video, and SMBIOS registration error paths.

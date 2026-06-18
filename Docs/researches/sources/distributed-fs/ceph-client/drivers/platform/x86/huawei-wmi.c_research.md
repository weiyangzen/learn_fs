# sources/distributed-fs/ceph-client/drivers/platform/x86/huawei-wmi.c

Purpose: Huawei laptop WMI extras driver supporting hotkeys, mic mute LED, battery charge thresholds, Fn-lock state, and debugfs WMI calls.

Important APIs/types/functions: GUIDs are `HWMI_METHOD_GUID`, `HWMI_EVENT_GUID`, and legacy WMI0 GUIDs. `huawei_wmi_cmd()` is the main method wrapper, normalizing package and legacy buffer response formats. DMI quirks control battery reset, EC micmute, and brightness key reporting. Battery support uses an ACPI battery hook plus threshold sysfs files; input uses sparse keymap; LED support registers `platform::micmute`; debugfs exposes raw argument/call.

Control flow: init allocates global state, applies DMI and module-parameter quirks, registers a platform driver and device. Probe installs notify handlers for present event GUIDs. If the method GUID exists, it initializes the WMI mutex, LED, Fn-lock, battery threshold support, and debugfs. Notifications process either direct integer scan codes or legacy code `0x80` by querying the expensive WMI block.

State and persistence: global `huawei_wmi` holds availability flags, debugfs argument, LED device, mutex, and device pointer. Battery thresholds, Fn-lock, and LED state are firmware/EC-backed; debugfs argument is runtime-only.

Dependencies and integration: ACPI WMI, ACPI battery hooks, power_supply devices, LED class, input sparse keymap, debugfs, DMI, EC helpers, and platform bus.

Risks: `huawei_wmi_cmd()` temporarily advances `obj->buffer.pointer` before freeing `out.pointer`, which relies on freeing the original ACPI object pointer rather than the adjusted inner pointer. Battery threshold discovery scans for nonzero bytes and may be fragile across firmware formats. Test signals include both package and 0x104 buffer responses, double-call retry behavior, battery-reset quirk, Fn-lock get/set, EC and WMI micmute paths, brightness reporting quirk, legacy WMI0 hotkey translation, and debugfs cleanup.

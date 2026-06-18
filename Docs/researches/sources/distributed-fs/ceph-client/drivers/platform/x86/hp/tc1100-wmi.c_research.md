# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/tc1100-wmi.c

Purpose: legacy HP Compaq TC1100 tablet WMI extras driver exposing wireless and jogdial state toggles through sysfs.

Important APIs/types/functions: WMI GUID `C364AC71-36DB-495A-8494-B439D472A505` provides two block instances: wireless and jogdial. `get_state()` maps raw WMI integer values to booleans; `set_state()` maps booleans back to firmware values and calls `wmi_set_block()`. The `show_set_bool` macro defines `wireless` and `jogdial` device attributes. PM hooks save and restore both states.

Control flow: init checks the GUID, allocates/adds a simple platform device, then probes a platform driver to create the sysfs group. Sysfs reads query WMI block state; writes parse an integer with `simple_strtoul()` and set WMI block state. Suspend reads both states into `suspend_data`; resume writes them back.

State and persistence: runtime state is the platform device and optional saved suspend values. Actual wireless/jogdial configuration is in firmware.

Dependencies and integration: ACPI WMI, platform device/driver model, sysfs attributes, and PM core.

Risks: the macro treats positive Linux error returns as ACPI-style status in places, but negative errors still route to read/write failure output. Write parsing is permissive because any nonzero value becomes enabled. Test signals include absent GUID, invalid instance handling, sysfs read/write mapping, suspend/resume preservation, and cleanup after platform probe failure.

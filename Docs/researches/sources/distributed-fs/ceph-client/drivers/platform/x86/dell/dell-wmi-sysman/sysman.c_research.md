## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/sysman.c

Purpose: top-level Dell WMI System Management driver. It creates `/sys/class/firmware-attributes/dell-wmi-sysman`, enumerates BIOS attribute WMI instances, builds per-attribute sysfs kobjects, and coordinates reset/pending-reboot/global state.

Important APIs/functions: global `wmi_priv` holds all shared state. `populate_string_buffer()`, `calculate_string_buffer()`, `calculate_security_buffer()`, and `populate_security_buffer()` build firmware command buffers. `map_wmi_error()` maps Dell firmware status to errno. `reset_bios_show/store()` and `pending_reboot_show()` implement top-level sysfs attributes. `get_wmiobj_pointer()` and `get_instance_count()` enumerate WMI blocks. `init_bios_attributes()` is the core enumerator: validates ACPI packages, skips empty/duplicate names, creates kobjects, and delegates population by type. `release_attributes_data()` tears down sysfs and metadata.

Control flow: module init verifies a Dell/Alienware OEM string, registers BIOS attribute and password WMI interface drivers, creates the firmware-attributes class device and `attributes`/`authentication` ksets, adds top-level files, then initializes enum, integer, string, and password-object attributes in order. Exit reverses the process.

State and persistence: global metadata arrays, password buffers, ksets, WMI device pointers, and `pending_changes` persist while the module is loaded. Firmware attribute changes and BIOS reset operations persist in BIOS and may require reboot; `pending_reboot` exposes the module's pending-change flag.

Dependencies and integration: WMI, DMI OEM-string detection, sysfs/kobject/kset APIs, NLS UTF-8 to UTF-16 conversion, firmware-attributes class, and the per-type attribute objects.

Risks: initialization has many partial-failure paths; cleanup must match created ksets/files. Duplicate attribute names are skipped. Password/security data is kept globally. Test signals include non-Dell rejection, missing WMI set/pass interfaces, malformed packages by type, duplicate names, reset modes, pending-reboot uevents, and complete module unload cleanup.

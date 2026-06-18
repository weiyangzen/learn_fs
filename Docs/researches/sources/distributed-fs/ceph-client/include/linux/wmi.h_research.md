# sources/distributed-fs/ceph-client/include/linux/wmi.h

## Purpose
`wmi.h` declares the Linux ACPI WMI driver interface. It models WMI devices, buffers and strings, method/procedure/block helpers, and the driver registration API for GUID-matched WMI drivers.

## Important APIs, Types, and Functions
`struct wmi_device` embeds `struct device` and records whether the Set Control Method is available. `to_wmi_device()` casts device pointers. `struct wmi_buffer` holds byte buffers, and `struct wmi_string` represents UTF-16LE WMI strings. Conversion helpers are `wmi_string_to_utf8s()` and `wmi_string_from_utf8s()`. Device helpers include `wmidev_invoke_method()`, `wmidev_invoke_procedure()`, `wmidev_query_block()`, `wmidev_set_block()`, raw ACPI evaluate/query/set helpers, and `wmidev_instance_count()`. `struct wmi_driver` embeds `device_driver`, ID table, minimum event size, singleton policy, and callbacks for probe/remove/shutdown and old/new notifications. Registration helpers are `__wmi_driver_register()`, `wmi_driver_unregister()`, `wmi_driver_register()`, and `module_wmi_driver()`.

## Control Flow
The WMI core discovers ACPI WMI GUID devices, creates `wmi_device` objects, matches them against driver ID tables, and invokes probe. Drivers call method/procedure/query/set helpers for instance and method IDs. Events are delivered through either deprecated ACPI-object notification callbacks or the newer aligned `wmi_buffer` callback with minimum size validation.

## State and Persistence
State is device-model WMI state discovered from ACPI tables and runtime driver binding state. Buffers are transient per method/event call. ACPI firmware may persist platform state behind WMI methods, but this header only defines kernel-side access.

## Dependencies and Integration Points
Dependencies include compiler attributes, device model, ACPI, module device tables, module ownership, and UTF conversion helpers. Integration points include platform/laptop drivers, firmware hotkeys, thermal/battery/vendor controls, ACPI method evaluation, and module registration.

## Risks
WMI method IDs, instance counts, and buffer sizes are firmware-specific. Drivers must validate event payload sizes and use `min_event_size`. UTF-16 string conversion must respect byte/character lengths. Deprecated notify callbacks expose raw ACPI objects and weaker alignment guarantees. Singleton policy matters for multi-instance GUIDs.

## Test Signals
Signals include ACPI WMI device enumeration, GUID match/probe/remove, method/procedure/query/set success and error paths, event delivery through `notify_new`, string conversion tests, multi-instance devices, and module unload cleanup.

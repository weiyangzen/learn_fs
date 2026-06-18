## sources/distributed-fs/ceph-client/drivers/platform/x86/gigabyte-wmi.c

Purpose: exposes Gigabyte motherboard temperature sensors through hwmon using WMI GUID `DEADBEEF-2001-0000-00A0-C90629100000`.

Important APIs/functions: `enum gigabyte_wmi_commandtype` includes firmware information queries and the implemented `GIGABYTE_WMI_TEMPERATURE_QUERY`. `struct gigabyte_wmi_args` carries one `u32 arg1`, used as the sensor index. `gigabyte_wmi_perform_query()` wraps `wmidev_evaluate_method()`. `gigabyte_wmi_query_integer()` validates integer ACPI results. `gigabyte_wmi_temperature()` queries a sensor, treats zero as absent, and converts the signed 8-bit value to millidegrees Celsius. HWMON ops use `gigabyte_wmi_hwmon_read()` and `gigabyte_wmi_hwmon_is_visible()`.

Control flow: probe detects usable sensors by querying all six possible channels and setting `usable_sensors_mask`. If no sensors work, probe returns `-ENODEV`; otherwise it registers hwmon device `gigabyte_wmi` with six possible temp inputs and visibility controlled by the mask.

State and persistence: module-global `usable_sensors_mask` records channels usable for the probed device. Sensor values are read live from firmware; no settings are written or persisted.

Dependencies and integration: WMI device driver API, ACPI object parsing, hwmon channel-info macros, and module WMI device table.

Risks: `usable_sensors_mask` is global even though WMI driver infrastructure could theoretically probe multiple devices. Temperature is cast to `s8`, so firmware values outside signed 8-bit semantics would be misread. Zero temperature is treated as absent, which may hide a legitimate 0 C reading but is likely a firmware sentinel. Test signals include systems with no sensors, partial channel availability, negative temperatures, WMI ACPI type mismatch, repeated hwmon reads, and multi-device behavior.

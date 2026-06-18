## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-ddv.c

Purpose: exposes Dell DDV WMI sensor and battery data through hwmon, ACPI battery extensions, sysfs ePPID attributes, and debugfs raw buffers. It supports DDV interface versions 2 and 3 unless `force` is set.

Important APIs, types, and functions: `enum dell_ddv_method` enumerates DDV WMI method IDs for battery, fan, thermal, analytics, and interface-version queries. `dell_wmi_ddv_query_type()`, `_integer()`, `_buffer()`, and `_string()` wrap `wmidev_evaluate_method()` with ACPI type and package validation. `struct dell_wmi_ddv_sensors` caches fan/thermal package objects for one second under a mutex. `dell_wmi_ddv_hwmon_add()` builds dynamic hwmon channel info from detected fan and thermal entries. Battery support uses `struct acpi_battery_hook`, `power_supply_register_extension()`, `dell_wmi_ddv_battery_translate()`, and property handlers for health, temperature, and manufacture date.

Control flow: probe reads interface version, allocates device data, creates debugfs entries, registers a battery hook if ACPI battery is reachable, and registers hwmon if sensors are available. HWMON reads refresh cached WMI buffers, validate channel indexes, then decode packed fan RPM or temperature records. Battery property reads translate a Linux `power_supply` to Dell battery index by serial number and then query the requested method.

State and persistence: sensor buffers are cached per device and invalidated on resume. Battery translation cache maps up to three Dell indexes to `power_supply` pointers and is invalidated on battery removal. No firmware settings are persisted; data is read-only.

Dependencies and integration: WMI, ACPI battery hook, power-supply extension API, hwmon, debugfs, PM sleep hooks, unaligned access helpers, and Dell firmware-specific DDV package formats.

Risks: firmware package shape is critical; `_query_buffer()` rejects mismatched count/type/size and warns on inconsistent lengths. Serial translation must handle decimal and hexadecimal ACPI serial strings. Manufacturer-access health decoding may see unknown subcodes. Test signals include supported/unsupported interface versions, systems with no sensors, fan/temp labels and values, debugfs raw files, battery ePPID lengths, health-code mapping, cache invalidation after resume, and hot-remove battery paths.

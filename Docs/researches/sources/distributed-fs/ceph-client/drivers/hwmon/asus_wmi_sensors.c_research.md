# sources/distributed-fs/ceph-client/drivers/hwmon/asus_wmi_sensors.c

Purpose: ASUS Ryzen-era motherboard hwmon driver that enumerates sensors through the ASUS WMI monitoring GUID and exposes them as hwmon voltage, temperature, fan, current, and water-flow channels.

Important APIs, types, and functions: `asus_wmi_sensor_info` stores WMI ID, class, location, name, source, type, and cached value. `asus_wmi_wmi_info` holds per-source timestamps, channel tables by hwmon type, and an `info_by_id` lookup. `asus_wmi_call_method()` wraps `wmi_evaluate_method()`. `asus_wmi_get_version()`, `asus_wmi_get_item_count()`, `asus_wmi_sensor_info()`, `asus_wmi_update_buffer()`, and `asus_wmi_get_sensor_value()` implement the firmware protocol. `asus_wmi_configure_sensor_setup()` enumerates sensors twice to count and then allocate/populate hwmon channel tables.

Control flow: the WMI driver probes only when the ASUS monitoring GUID is present and the board matches the DMI allowlist. Probe checks interface version and sensor count, initializes the cache mutex, enumerates supported sensor classes, builds channel info arrays and sensor pointers, then registers `asus_wmi_sensors`. Reads fetch the sensor pointer for type/channel, refresh all sensors sharing that sensor source once per second using QWEC then RWEC reads, scale units, and return labels from firmware names.

State and persistence: cached values live in each `asus_wmi_sensor_info`, with `source_last_updated[source]` controlling refresh granularity. The mutex protects cache updates. No persistent hardware configuration is written; the driver is read-only.

Dependencies and integration points: depends on WMI, ACPI object parsing, DMI board matching, hwmon core, mutexes, jiffies, and unit helpers. The driver maps ASUS firmware sensor classes to hwmon classes and assumes source IDs fit the fixed `source_last_updated[3]` array.

Risks: firmware packages must have exactly five elements and valid string/integer types. Unsupported or new sensor classes are ignored. `source` values outside the small timestamp array would be unsafe if firmware returns unexpected data. Enumeration is performed twice and failed second-pass sensor reads are skipped, which can reduce channel population relative to initial counts. Unit scaling assumes WMI voltage is microvolts, temperature Celsius, current amperes, and fans/flow already hwmon-ready.

Test signals: use DMI-allowed ASUS X370/X470/B450/X399 boards; verify version >= 2, sensor count, names, channel order, source-specific cache refresh, and WMI error handling. Tests should simulate malformed ACPI objects, unsupported classes, changing sensor counts, and source IDs. Compare reported values against firmware/BIOS tools for scaling.

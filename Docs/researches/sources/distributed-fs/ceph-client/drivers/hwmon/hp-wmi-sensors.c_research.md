# sources/distributed-fs/ceph-client/drivers/hwmon/hp-wmi-sensors.c

## Purpose
`hp-wmi-sensors.c` exposes numeric sensors on HP business-class systems through WMI. It maps HP BIOS WMI objects into hwmon temperature, voltage, current, fan, and intrusion attributes, includes debugfs introspection, and optionally subscribes to WMI events for alarms.

## Important APIs, Types, and Functions
Key structures are `hp_wmi_numeric_sensor`, `hp_wmi_platform_events`, `hp_wmi_event`, `hp_wmi_info`, and `hp_wmi_sensors`. Property maps validate ACPI object layouts. String helpers handle normal ACPI strings and raw length-prefixed UTF-16 WMI buffers. `check_numeric_sensor_wobj()` supports both old and new object layouts, including flattened `PossibleStates[]`. `populate_*_from_wobj()` and `update_numeric_sensor_from_wobj()` load and refresh WMI data. `classify_numeric_sensor()`, `scale_numeric_sensor()`, and `numeric_sensor_has_fault()` translate HP semantics to hwmon. `hp_wmi_hwmon_*()` implement the hwmon callbacks. Event helpers classify and match fan, temperature, and intrusion events.

## Control Flow
Probe allocates state for the WMI device, initializes a mutex, and calls `hp_wmi_sensors_init()`. Initialization loads platform event descriptors, enumerates numeric sensor instances, filters disconnected/unsupported sensors, classifies connected sensors into hwmon channel maps, creates debugfs when enabled, finds which events can back alarm attributes, installs a WMI notify handler if useful, builds dynamic `hwmon_channel_info` arrays, and registers `hp_wmi_sensors`. Hwmon reads update each sensor at most once per second via `wmidev_block_query()`, then return scaled values, fault state, labels, alarm flags, or intrusion status.

## State and Persistence
Sensor metadata is devm-managed for the WMI device lifetime. Current readings, current state, unit modifier, cached scaled values, last update times, alarm flags, and intrusion state live in RAM. Reading temp/fan alarm clears that per-channel alarm flag; writing zero to intrusion clears intrusion state. No firmware settings are changed.

## Dependencies and Integration Points
The driver integrates with the WMI bus, ACPI object parsing, hwmon callback registration, thermal zone registration through `HWMON_C_REGISTER_TZ`, debugfs, jiffies, mutexes, and unit conversion helpers.

## Risks
The WMI schemas are firmware-defined and partly reverse-engineered; validation must stay strict to avoid misparsing flattened packages. `hp_wmi_chip_info` is static but its `.info` pointer is assigned per probe, which is risky if multiple WMI devices existed concurrently. Event-to-sensor matching relies on free-form names/descriptions. Alarm reads clear flags, so polling consumers can race each other. The update path ignores refreshes within one second even if an event just occurred.

## Test Signals
Test old and new numeric sensor package layouts, raw UTF-16 string conversion, disconnected sensor filtering, unit scaling for C/F/K and modifier extremes, dynamic channel configs, debugfs contents, WMI event parsing and alarm matching, intrusion clear semantics, thermal-zone registration for temps, and failure tolerance when notify handler installation fails.

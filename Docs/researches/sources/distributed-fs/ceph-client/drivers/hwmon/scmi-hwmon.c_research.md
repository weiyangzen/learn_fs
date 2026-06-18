# sources/distributed-fs/ceph-client/drivers/hwmon/scmi-hwmon.c

Purpose: hwmon bridge for ARM SCMI sensor protocol. It discovers firmware-described sensors, maps supported classes to hwmon channels, scales readings into Linux hwmon units, and registers thermal zones for temperature sensors.

Important APIs/types/functions: `struct scmi_sensors` stores protocol handle and per-hwmon-type sensor arrays. `scmi_hwmon_scale()` adjusts sensor readings using SCMI scale plus class-specific milli/micro units. `scmi_hwmon_probe()` builds dynamic channel info and sensor arrays. `scmi_thermal_sensor_register()` attaches temperature sensors to thermal zones.

Control flow: probe obtains SCMI sensor ops, counts sensors, counts supported classes, allocates channel tables, fills per-type sensor arrays in stable order, registers hwmon, enables temperature sensors via `config_set()`, then tries thermal zone registration.

State and persistence: discovered sensor pointers and protocol handle persist for device lifetime. Readings are not cached. Temperature sensors are explicitly enabled after hwmon registration.

Dependencies/integration: SCMI protocol core, hwmon info API, thermal OF zones, sysfs labels from firmware sensor names.

Risks: `sensor_ops` is file-global even though probe stores protocol handles per device. Thermal enabling uses loop index `i` from hwmon temp array rather than `sensor->id`, which should be validated against SCMI expectations. Scaling rejects absolute scale over 19.

Test signals: mixed sensor-class discovery, labels, scaled units, thermal-zone attachment and ENODEV skip path, config_set failures, and unsupported sensor classes being ignored.

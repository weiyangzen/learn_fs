# sources/distributed-fs/ceph-client/drivers/hwmon/scpi-hwmon.c

Purpose: hwmon bridge for ARM SCPI sensor protocol. It dynamically creates sysfs attributes for SCPI sensors, scales readings to hwmon units, and optionally registers temperature sensors with thermal zones.

Important APIs/types/functions: `struct sensor_data` stores SCPI info, scale, generated input/label attributes, and attribute names. `scpi_scale_reading()` normalizes firmware values. `scpi_show_sensor()` and `scpi_show_label()` back generated sysfs attributes. `scpi_hwmon_probe()` builds all attributes from firmware sensor metadata.

Control flow: probe obtains SCPI ops, reads sensor capability count, allocates sensor and attribute arrays, selects scale table from OF compatible, iterates sensors, assigns hwmon names by class, initializes attributes, registers hwmon with groups, then registers thermal zones for temperature sensors.

State and persistence: sensor metadata, generated attribute names, and scaling factors persist. Sensor values are read live on every sysfs access.

Dependencies/integration: SCPI protocol ops, OF match data, hwmon group API, thermal OF zones.

Risks: unsupported sensor classes leave holes in `data[]`; later thermal-zone loop iterates `nr_sensors` rather than the populated `idx`, so uninitialized entries can be examined. Uses `sprintf` rather than `sysfs_emit`. Thermal registration errors are ignored.

Test signals: OF scale selection including Amlogic variant, generated attribute names and labels for each class, signed temperature output, unsupported class handling, and thermal-zone registration.

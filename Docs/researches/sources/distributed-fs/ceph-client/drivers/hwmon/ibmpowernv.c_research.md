# sources/distributed-fs/ceph-client/drivers/hwmon/ibmpowernv.c

## Purpose

`ibmpowernv.c` exports IBM PowerNV OPAL platform sensors as hwmon attributes. It translates OPAL device-tree sensor nodes into hwmon names for fan, temperature, voltage, power, current, and energy sensors, reads values through OPAL firmware, and optionally exposes sensor-group enable controls.

## Important APIs, Types, and Functions

`enum sensors` indexes global `sensor_groups[]`, each of which accumulates a hwmon attribute group. `struct sensor_data` stores an OPAL sensor id, hwmon index, OPAL index, type, label, sysfs name, attribute object, and optional group data. `struct sensor_group_data` stores group id, mutex, and enabled state. `show_sensor()`, `show_label()`, `show_enable()`, and `store_enable()` implement sysfs operations. Parsing helpers include `get_sensor_type()`, `parse_opal_node_name()`, `get_sensor_index_attr()`, and `convert_opal_attr_name()`. `populate_attr_groups()` counts attributes, while `create_device_attrs()` allocates and fills the final attribute arrays.

## Control Flow

Probe allocates `platform_data`, stores it as driver data, counts sensors and optional labels/min/max/group controls from `/ibm,opal/sensors` and `ibm,opal-sensor-group` nodes, allocates attribute arrays per sensor type, then walks the sensor tree again to populate `sensor_data` entries. Legacy node names such as `cooling-fan#2-data` are parsed into indexed hwmon attributes; newer nodes fall back to sequential `*_input` naming. Reads call `opal_get_sensor_data_u64()`, then scale temperature to millidegrees and power input to microwatts. Group enable writes serialize on a per-group mutex and call `sensor_group_enable()`.

## State and Persistence Behavior

Driver state is devm-managed for the platform device lifetime. Global `sensor_groups[]` holds mutable counters and hwmon index state during probe. Per-group enable state is cached in memory after successful OPAL calls and defaults false until the first matching sensor enables the group during attribute creation. Sensor values are not cached by this driver.

## Dependencies and Integration Points

The driver is PowerNV/OPAL-specific and depends on Open Firmware device tree parsing, OPAL sensor calls, OPAL sensor-group control, PowerPC CPU/PIR mapping helpers for labels, platform driver matching by `opal-sensor`, and devm hwmon group registration. It bridges firmware sensor metadata into the standard hwmon sysfs ABI.

## Risks and Edge Cases

`of_find_node_by_path("/ibm,opal/sensors")` is not checked before child iteration, so missing OPAL sensor nodes rely on iterator behavior. `sensor_groups[]` is global mutable state; repeated probe/unbind cycles or multiple devices could inherit stale counts or indices. Group discovery increments attribute counts once per group and later creates enable attributes once per type/group, so malformed phandles can skew counts. OPAL errors from reads are returned directly to sysfs. Labels are truncated to fixed buffers. Compatibility with newer device trees depends on `sensor-type` strings exactly matching `sensor_groups[].name`.

## Test Signals

Validate legacy and new device-tree naming, label formatting with `ibm,pir` and `ibm,chip-id`, min/max attribute creation, group enable toggling and mutex behavior, OPAL read error propagation, unit scaling for temperature and power, missing sensor-id fallback to `sensor-data`, and reprobe behavior to detect stale global group state.

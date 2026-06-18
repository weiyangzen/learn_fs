# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_hwmon.c

## Purpose
`igb_hwmon.c` provides optional `CONFIG_IGB_HWMON` integration for exposing igb thermal sensor data through the Linux hwmon sysfs interface. It creates per-sensor attributes for label, temperature input, caution threshold, and max/critical threshold, creates an I2C client for the i350 thermal sensor endpoint, and registers a hwmon device with attribute groups.

## Important APIs, Types, and Functions
The file defines `i350_sensor_info` with I2C board info for `"i350bb"`. Sysfs show callbacks are `igb_hwmon_show_location`, `igb_hwmon_show_temp`, `igb_hwmon_show_cautionthresh`, and `igb_hwmon_show_maxopthresh`. `igb_add_hwmon_attr` constructs one `struct hwmon_attr` entry and appends it to the adapter's `struct hwmon_buff`. The externally used entry points are `igb_sysfs_init` and `igb_sysfs_exit`; `igb_sysfs_del_adapter` is currently empty because devm-managed resources handle teardown.

## Control Flow
`igb_sysfs_init` first checks whether `adapter->hw.mac.ops.init_thermal_sensor_thresh` exists. It calls that operation, exits if no sensors are present or initialization fails, allocates `struct hwmon_buff` with `devm_kzalloc`, and loops over `E1000_MAX_SENSORS`. For each sensor with nonzero location, it adds caution, label, input, and max attributes. It then creates an I2C client on `adapter->i2c_adap`, attaches the attribute group, and registers the hwmon device through `devm_hwmon_device_register_with_groups`. Attribute reads dereference the stored sensor pointer; temperature reads refresh sensor data by calling `get_thermal_sensor_data` before returning millidegrees.

## State and Persistence
State is stored in `adapter->igb_hwmon_buff`, `adapter->i2c_client`, and the MAC thermal sensor data under `adapter->hw.mac.thermal_sensor_data`. Sysfs attributes are read-only (`0444`) and do not persist configuration. Sensor thresholds come from MAC initialization and are reported in millidegrees Celsius. Resource lifetime is device-managed, so teardown is mostly implicit.

## Dependencies and Integration Points
This code depends on `igb.h` hwmon structs, `e1000_82575.h` thermal sensor definitions, MAC operations for initializing thresholds and fetching live sensor data, Linux I2C APIs, sysfs attribute APIs, and hwmon registration. It is called from main adapter setup/teardown when `CONFIG_IGB_HWMON` is enabled.

## Risks
Risks include stale or missing MAC thermal callbacks, incorrect sensor count assumptions, failure partway through attribute construction, and the empty explicit deletion helper relying on devm lifetime. Attribute names use a 12-byte buffer and must continue to fit strings like `tempN_input` for the supported sensor count. I2C client creation failure prevents hwmon registration even if internal thermal registers are readable.

## Test Signals
Signals include successful probe with hwmon enabled, `/sys/class/hwmon` entries named after the i350 client, correct `tempN_label`, `tempN_input`, `tempN_max`, and `tempN_crit` files for present sensors only, temperature values changing after `get_thermal_sensor_data`, clean removal/unbind without sysfs warnings, and successful builds with `CONFIG_IGB_HWMON` both enabled and disabled.

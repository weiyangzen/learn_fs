# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sysfs.c

## Purpose
`ixgbe_sysfs.c` registers hwmon sysfs attributes for ixgbe thermal sensors. It creates read-only temperature label, input, max, and critical files for sensors reported by MAC thermal-sensor operations.

## Important APIs and functions
The public entry points are `ixgbe_sysfs_init` and `ixgbe_sysfs_exit`, called from ixgbe main driver code. `ixgbe_add_hwmon_attr` builds one `device_attribute` for a selected sensor and type. Show callbacks are `ixgbe_hwmon_show_location`, `ixgbe_hwmon_show_temp`, `ixgbe_hwmon_show_cautionthresh`, and `ixgbe_hwmon_show_maxopthresh`.

## Control flow
Initialization first checks whether `init_thermal_sensor_thresh` exists. It calls that MAC op and exits if no thermal sensors are present or initialization fails. It allocates `struct hwmon_buff` with `devm_kzalloc`, iterates `IXGBE_MAX_SENSORS`, skips sensors with location zero, and adds four read-only attributes for each meaningful sensor. It then registers the group with `devm_hwmon_device_register_with_groups`.

The temperature show callback refreshes sensor data through `get_thermal_sensor_data`, reads the cached temperature, converts degrees to millidegrees, and prints a decimal value. Threshold callbacks print cached caution and maximum operating thresholds in millidegrees. Location prints `locN`.

## State and persistence
The runtime state is `adapter->ixgbe_hwmon_buff`, containing attribute descriptors, names, attribute pointers, group data, and an `n_hwmon` counter. Each attribute points at one `adapter->hw.mac.thermal_sensor_data.sensor[offset]`. Device-managed allocation and registration tie cleanup to the device; `ixgbe_sysfs_del_adapter` is empty and `ixgbe_sysfs_exit` is effectively a stub.

## Dependencies and integration points
The file depends on Linux sysfs, kobject, device, netdevice, and hwmon APIs, plus ixgbe MAC thermal-sensor ops and sensor data structures. It integrates with probe/remove paths and exposes values under the kernel hwmon interface rather than custom netdev attributes.

## Risks and edge cases
The code assumes the hwmon buffer has enough preallocated entries for four attributes per populated sensor. If a MAC reports many sensors but the backing arrays are too small in the struct definition, attributes could overflow. A failure after some attributes are added exits before registration, relying on devm cleanup for allocated memory. The empty delete hook is acceptable for devm-managed hwmon but would be insufficient if non-devm registration were introduced.

## Test signals
Tests should validate no hwmon device appears when thermal ops are absent or report no sensors, all expected `tempN_*` attributes appear for populated sensors, values are in millidegrees, `get_thermal_sensor_data` is called on temperature reads, registration failure propagates an error, and driver remove/unbind cleans up hwmon entries through devm.

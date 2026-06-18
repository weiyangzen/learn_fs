# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/hwmon.c

## Purpose
`hwmon.c` registers mlx5 temperature sensors with the Linux hwmon framework. It discovers ASIC/platform and optional module sensors, reads current/highest/critical temperatures through MTMP, enables maximum-temperature tracking, and supports resetting max-temperature history.

## Important APIs, Types, And Functions
- `struct mlx5_hwmon` stores the mlx5 device, registered hwmon device, channel metadata/config arrays, chip info, sensor descriptors, and sensor counts.
- `mlx5_hwmon_query_mtmp`, `mlx5_hwmon_reset_max_temp`, and `mlx5_hwmon_enable_max_temp` access MTMP.
- hwmon callbacks `mlx5_hwmon_read`, `mlx5_hwmon_write`, `mlx5_hwmon_is_visible`, and `mlx5_hwmon_read_string` implement temp attributes.
- Discovery helpers read MTCAP sensor count/map, derive module sensor index from module number, test module monitoring capability, allocate arrays, and initialize sensor names.
- Public lifecycle is `mlx5_hwmon_dev_register`, `mlx5_hwmon_dev_unregister`, and `hwmon_get_sensor_name`.

## Control Flow And State
Registration first checks MTMP access-register support. Allocation reads sensor count, probes the module sensor by reading its mapped MTMP temperature, allocates descriptor/config arrays for platform plus optional module sensor, and stores `mdev`. Device init reads MTCAP, builds hwmon channel info, fills sensor indexes from the sensor map plus module index, queries names or synthesizes `sensor<index>`, enables max temperature on each channel, and registers `hwmon_device_register_with_info`.

Reads query MTMP for the channel's sensor index and convert firmware units of 0.125 C to millidegrees C. Writes only support `hwmon_temp_reset_history`, which sets MTMP `mtr`.

## State And Persistence Behavior
Software state is stored at `mdev->hwmon` until unregister. Hardware state includes MTMP max-temperature tracking enable and reset-history side effects. Sensor values are live firmware register reads; the driver does not cache temperatures.

## Dependencies And Integration Points
The file depends on `CONFIG_HWMON`, Linux hwmon APIs, mlx5 access-register helpers, MTCAP/MTMP register layouts, and port module-number query support. It integrates with core device registration and can supply sensor names to other mlx5 diagnostics.

## Risks And Edge Cases
Sensor count and sensor map must agree; otherwise channel indexes may not represent the intended sensors. Module monitoring is inferred from a nonzero temperature read, which can miss unsupported or temporarily unavailable modules. Name copying depends on firmware-provided fixed fields. Any MTMP error aborts registration.

## Test Signals
Check registration on devices with and without MTMP, platform sensors only, platform plus module sensor, readable labels/input/highest/crit attributes, reset-history writes, max-temp enable failures, and unregister clearing `mdev->hwmon`.

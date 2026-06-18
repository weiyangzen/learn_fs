# sources/distributed-fs/ceph-client/drivers/hwmon/intel-m10-bmc-hwmon.c

## Purpose

`intel-m10-bmc-hwmon.c` exposes telemetry from Intel MAX 10 BMC managed FPGA boards as hwmon attributes. It is table-driven for N3000, D5005, N5010, and N6000 board layouts, mapping board-specific BMC register offsets to temperature, voltage, current, and power channels with labels and threshold attributes.

## Important APIs, Types, and Functions

`struct m10bmc_sdata` describes one sensor channel: input, max, critical, hysteresis, min register offsets, multiplier, and label. `struct m10bmc_hwmon_board_data` maps hwmon sensor types to board tables and channel-info arrays. `struct m10bmc_hwmon` stores the parent MAX 10 BMC handle, selected board data, sanitized hwmon name, and chip info. `find_sensor_data()` selects a table entry. `do_sensor_read()` reads via `m10bmc_sys_read()`, handles invalid sentinel values, and applies scaling. `m10bmc_hwmon_read()` maps hwmon attributes to register offsets and computes hysteresis values. `m10bmc_hwmon_read_string()` returns labels. Probe selects board data from platform id driver data and registers hwmon.

## Control Flow

The MFD core instantiates a platform device with an id such as `n6000bmc-hwmon`. Probe retrieves the parent `intel_m10bmc`, picks board data from the id table, sets `hw->chip.info` and ops, sanitizes the board name, and registers the hwmon device. Reads are dispatched by hwmon core using the board-specific channel metadata. Unsupported attributes have zero register offsets and return `-EOPNOTSUPP`. Hysteresis attributes read both threshold and hysteresis registers and return threshold minus hysteresis.

## State and Persistence Behavior

The driver holds only devm-managed immutable table pointers and parent device references. It does not cache sensor values or write thresholds. Sensor validity is determined at read time. All board-specific behavior is encoded in static tables and channel-info arrays.

## Dependencies and Integration Points

It depends on the Intel MAX 10 BMC MFD core (`m10bmc_sys_read` and `struct intel_m10bmc`), platform-device id matching, modern hwmon info APIs, and the `INTEL_M10_BMC_CORE` namespace. It provides the hwmon child function of the larger MAX 10 BMC device stack.

## Risks and Edge Cases

Table and `HWMON_CHANNEL_INFO` ordering must match exactly; a mismatch would read the wrong register or label. All attributes are globally visible as read-only through `.visible = 0444`, so unsupported attributes rely on read-time `-EOPNOTSUPP` rather than visibility suppression. The firmware invalid sentinel `0xdeadbeef` maps to `-ENODATA`; real data with that raw value would be hidden. Multipliers are board-table-specific and must match firmware units. Hysteresis subtraction can produce negative values if firmware reports unexpected ordering.

## Test Signals

Test each platform id selects the right board table, channel counts match channel-info arrays, labels match expected board documentation, invalid sentinel returns `-ENODATA`, unsupported zero-offset thresholds return `-EOPNOTSUPP`, multiplier scaling for temperature and power, hysteresis subtraction, and parent MFD read failure propagation.

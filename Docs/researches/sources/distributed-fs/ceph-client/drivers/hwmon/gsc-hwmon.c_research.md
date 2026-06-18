# sources/distributed-fs/ceph-client/drivers/hwmon/gsc-hwmon.c

## Purpose
`gsc-hwmon.c` exposes Gateworks System Controller ADC, temperature, voltage, and fan channels as hwmon inputs. It can consume platform data or derive channel definitions from device tree, and optionally exposes automatic fan-control point attributes.

## Important APIs, Types, and Functions
`struct gsc_hwmon_data` owns the GSC parent pointer, platform data, regmap, per-type channel arrays, dynamic config arrays, `hwmon_channel_info` objects, and `hwmon_chip_info`. `gsc_hwmon_regmap_bus` adapts `gsc_read()`/`gsc_write()` to regmap. `gsc_hwmon_read()` converts channel register bytes according to `mode_temperature`, `mode_voltage_raw`, `mode_voltage_16bit`, `mode_voltage_24bit`, or `mode_fan`. `gsc_hwmon_read_string()` returns labels. `gsc_hwmon_get_devtree_pdata()` builds platform data from child nodes. Extra sysfs handlers expose six fan auto point temperatures and fixed PWM percentages.

## Control Flow
Probe gets parent `gsc_dev`, loads platform data or parses firmware child nodes, allocates state, initializes an 8-bit regmap on `gsc->i2c_hwmon`, partitions channels by mode into temp/in/fan arrays, builds config arrays with input and label bits, optionally attaches the fan auto-point attribute group if a fan base was found, then registers a callback-based hwmon device. Reads select the channel by type and index, bulk-read two or three bytes, combine little-endian-style by shifting each byte to its offset, and scale the result.

## State and Persistence
The driver keeps only static channel metadata and no measurement cache. Fan auto point writes persist in the controller registers. Device-tree voltage offsets are converted from microvolts to millivolts during parsing and stored in platform data.

## Dependencies and Integration Points
It integrates with the Gateworks MFD core, regmap, OF child nodes, platform data (`linux/platform_data/gsc_hwmon.h`), hwmon callback registration, and optional extra sysfs groups.

## Risks
The byte-combination loop depends on controller byte ordering and should be tested against real hardware. Temperature sign conversion uses `tmp > 0x8000` and subtracts `0xffff`, which is sensitive around the sign boundary. Auto-point sysfs appears whenever `fan_base` is set, independent of whether a fan channel exists. Invalid or excessive DT channels fail probe.

## Test Signals
Test DT parsing for labels, registers, modes, voltage dividers/offsets, per-type channel limits, raw scaling math, 16/24-bit voltage reads, fan RPM conversion, fan auto-point read/write clamping, and probe failure on invalid mode or missing child properties.

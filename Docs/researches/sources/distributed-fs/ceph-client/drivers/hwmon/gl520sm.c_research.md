# sources/distributed-fs/ceph-client/drivers/hwmon/gl520sm.c

## Purpose
`gl520sm.c` drives the Genesys Logic GL520SM monitor. It exports VDD/VIN voltages, two fan tachometers, temperature channels, alarms, beep controls, and CPU VID. One physical input can be configured as either a second temperature channel or a fifth voltage input.

## Important APIs, Types, and Functions
`struct gl520_data` stores I2C state, dynamic attribute groups, cached register values, `vrm`, `alarm_mask`, and `two_temps`. `gl520_read_value()` and `gl520_write_value()` wrap byte versus swapped-word SMBus access. `gl520_update_device()` refreshes cached sensor values every two seconds. `cpu0_vid_show()` uses `vid_from_reg()` and `vid_which_vrm()` from `hwmon-vid`. Sysfs handlers implement voltage, fan, temperature, alarm, beep, and `fan1_off` files. `extra_sensor_type` is a module parameter controlling autodetect versus forced temp/voltage for the shared input.

## Control Flow
Detection scans `0x2c` and `0x2d`, checks SMBus capabilities, chip ID `0x20`, revision masked to zero, and a clear reset bit. Probe allocates state, sets client data, and calls `gl520_init_client()`. Initialization chooses VRM, applies `extra_sensor_type` by modifying config bit `0x10`, enables monitoring, calls the update routine once, masks fan alarms whose minimum is zero, and writes a sanitized beep mask. Probe then registers the common sysfs group plus either `gl520_group_temp2` or `gl520_group_in4`.

## State and Persistence
The cache is RAM-only and marked valid after refresh. User writes change hardware threshold registers, fan divisors, fan-off state, beep enable, and beep masks. The shared input mode can be changed at module load and persists as a config register bit. `alarm_mask` is local policy derived partly from fan minimum registers.

## Dependencies and Integration Points
The driver uses I2C class probing, SMBus byte/word operations, hwmon sysfs helpers, and `hwmon-vid` for CPU VID presentation. It registers through `devm_hwmon_device_register_with_groups()` rather than the newer callback-based hwmon API.

## Risks
The extra sensor mode is a global module parameter, so a forced choice affects all matching devices. Cache updates do not robustly propagate SMBus read errors. The same alarm/beep bit is used for `temp2` or `in4`, making attribute selection and masks dependent on mode. Read-modify-write register operations can race with firmware or other masters on the bus.

## Test Signals
Verify autodetect and forced extra sensor modes, correct sysfs group selection, voltage/temp/fan conversion and clamping, VID output across VRM values, invalid fan divisor rejection, fan minimum zero alarm masking, and stable behavior when a bus read/write returns an error.

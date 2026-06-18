# sources/distributed-fs/ceph-client/drivers/iio/light/cros_ec_light_prox.c

## Purpose

`cros_ec_light_prox.c` is an IIO frontend for ChromeOS EC light and proximity motion-sense sensors. It represents one logical light or proximity stream from the EC, plus timestamp, and delegates sampling, buffering, common attributes, and PM to `cros_ec_sensors_core`.

## Important APIs, Types, And Functions

`struct cros_ec_light_prox_state` embeds `struct cros_ec_sensors_core_state` and stores two IIO channel specs. `cros_ec_light_prox_read()` handles raw proximity, processed light, calibration bias, calibration scale, and delegates all other masks to `cros_ec_sensors_core_read()`. `cros_ec_light_prox_write()` handles calibration writes and delegates common writes. `cros_ec_light_prox_probe()` initializes the core, builds channel metadata based on EC motion sensor type, and registers the sensor with core callbacks.

## Control Flow

Probe allocates an IIO device, calls `cros_ec_sensors_core_init()` with capture support, selects channel type from `state->core.type`, populates scan type and sysfs masks, adds a timestamp channel, sets `read_ec_sensors_data` to `cros_ec_sensors_read_cmd`, and calls `cros_ec_sensors_core_register()`. Reads and writes take `core.cmd_lock`, prepare motion-sense host command parameters, and call the EC command helper. Light processed data is already lux from EC firmware; proximity raw data is returned directly.

## State And Persistence

State such as calibration offsets, range, sample frequency, and buffered capture state lives in the embedded EC core state and EC firmware. Writes update `core.calib`, `core.curr_range`, and `core.range_updated` after successful host commands. There is no local hardware register cache.

## Dependencies And Integration Points

The driver depends on ChromeOS EC protocol definitions, `cros_ec_sensors_core`, platform devices named `cros-ec-light` or `cros-ec-prox`, IIO triggered buffers through the core, and `cros_ec_sensors_pm_ops`. It is not a physical bus driver; it binds to EC-created platform devices.

## Risks And Test Signals

Channel count is fixed to one data channel plus timestamp even if EC firmware internally merges multiple sensors. Calibration bias code stores only `calib[0].offset` but reads `calib[idx].offset`, which is fine for one data channel but fragile if expanded. Tests should use EC emulation or hardware to verify processed light, raw proximity, calibration bias/scale host commands, sample-frequency availability, buffered captures, and PM callbacks supplied by the core.

# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors.c

Purpose: platform IIO driver for ChromeOS EC contiguous 3-axis physical sensors: accelerometers, gyroscopes, and magnetometers. It builds per-axis IIO channels and delegates shared host-command, buffer, FIFO, and ext-info handling to the core.

Important APIs, types, and functions: `struct cros_ec_sensors_state` embeds core state and a four-channel array. `cros_ec_sensors_read()` handles raw axis reads, calibration bias/scale reads, range-derived scale, sample frequency via core fallback, and unit conversion for accel/gyro/mag. `cros_ec_sensors_write()` writes calibration bias/scale, sensor range, and sample frequency through the core. `cros_ec_sensors_probe()` initializes core state, builds X/Y/Z channels according to `core.type`, adds timestamp, chooses LPC shared-memory read for accel/gyro when available or host-command reads otherwise, and registers FIFO push support.

Control flow: all direct reads/writes lock `core.cmd_lock`, set motion-sense subcommands, and call `cros_ec_motion_send_host_cmd()` or core helpers. Buffer data can arrive from EC FIFO through `cros_ec_sensors_push_data()` or from software trigger capture through `cros_ec_sensors_capture()`.

State and persistence: cached calibration arrays, current range, and range-updated flag live in core state. Actual calibration, ODR, and range settings are stored by the EC.

Dependencies and integration: depends on ChromeOS EC sensorhub, IIO core/buffer APIs, and platform ids `cros-ec-accel`, `cros-ec-gyro`, `cros-ec-mag`.

Risks and test signals: scale conversions must match IIO units and EC raw ranges. LPC memory layout supports only accel/gyro as coded. Tests should cover each sensor type, calibration fallback on older ECs, range resume restore, direct reads with both LPC and command paths, sample frequency available list, FIFO push, and channel scan indexes.

# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_lid_angle.c

Purpose: platform IIO driver for the ChromeOS EC lid-angle virtual sensor. It exposes a single angle channel plus timestamp and uses the common ChromeOS EC sensor core for host-command setup and registration.

Important APIs, types, and functions: `cros_ec_lid_angle_channels[]` defines an unsigned angle channel and software timestamp. `struct cros_ec_lid_angle_state` embeds the core state. `cros_ec_sensors_read_lid_angle()` sends `MOTIONSENSE_CMD_LID_ANGLE` and copies the EC response value. `cros_ec_lid_angle_read()` handles direct raw reads under `core.cmd_lock`. `cros_ec_lid_angle_probe()` initializes the core as a non-physical device, installs triggered-buffer capture using `cros_ec_sensors_capture`, sets the read callback, and registers the IIO device.

Control flow: direct reads and triggered-buffer captures both call the same `read_ec_sensors_data` callback. The generic core capture path reads active scan data and pushes timestamped buffers.

State and persistence: there is no mutable sensor state beyond core command buffers and callback pointers. The lid angle is computed by the EC and read on demand.

Dependencies and integration: depends on platform device ids for `cros-ec-lid-angle`, `cros_ec_sensors_core_init/register`, and IIO triggered-buffer support.

Risks and test signals: the driver assumes the EC command is available when the platform device exists. Tests should cover direct angle reads, triggered capture path, EC command failure warnings, channel scan layout, and probe cleanup on buffer setup failure.

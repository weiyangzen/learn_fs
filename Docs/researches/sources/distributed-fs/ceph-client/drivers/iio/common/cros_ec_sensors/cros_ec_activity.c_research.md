# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_activity.c

Purpose: platform IIO driver for ChromeOS EC activity sensors, including body detection proximity and significant-motion activity events. It uses the ChromeOS EC sensor core for host-command transport and IIO registration.

Important APIs, types, and functions: `struct cros_ec_sensors_state` embeds core state and dynamic channel metadata. `cros_ec_activity_sensors_read_raw()` reads body-detection state and returns inverted proximity semantics. `cros_ec_activity_read_event_config()` lists enabled activities; `cros_ec_activity_write_event_config()` enables/disables activity reporting. `cros_ec_activity_push_data()` translates EC activity FIFO data into IIO events with the correct channel index and event direction. `cros_ec_sensors_probe()` initializes core state, lists supported activities, builds one channel per supported activity plus timestamp, and registers with `cros_ec_sensors_core_register()`.

Control flow: probe asks the EC for all enabled/disabled activities, creates proximity or activity channels, attaches limited ext-info, then registers a FIFO push callback. Runtime reads and event config commands lock `core.cmd_lock`, set the relevant motion-sense subcommand, and call `cros_ec_motion_send_host_cmd()`. FIFO updates call back into `cros_ec_activity_push_data()` and emit IIO events rather than regular samples.

State and persistence: channel indexes for body detection and significant motion are cached in driver state. Activity enable state is stored by the EC and queried/written via host commands.

Dependencies and integration: depends on ChromeOS EC sensor core, platform data/proto commands, IIO events, and the EC sensorhub FIFO callback path.

Risks and test signals: unknown activity bits are warned and skipped; index handling must remain consistent when multiple activities are present. Tests should cover body detection raw inversion, event enable read/write, significant-motion event direction, unknown activities, no-activity `-ENODEV`, and FIFO event delivery with timestamps.

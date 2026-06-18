# sources/distributed-fs/ceph-client/drivers/hwmon/occ/common.c

Purpose: shared OCC hwmon implementation. It sends poll and power-cap commands through a transport callback, parses OCC poll responses, dynamically creates sensor sysfs attributes, rate-limits updates, tracks communication/safe-state errors, and registers/unregisters the hwmon device.

Important APIs/types/functions: transport-facing exports are `occ_setup()`, `occ_shutdown()`, `occ_active()`, and `occ_update_response()`. Internals include OCC sensor format structs, `occ_poll()`, `occ_set_user_power_cap()`, typed show functions for TEMP/FREQ/POWR/CAPS/EXTN versions, `occ_init_attribute()`, `occ_setup_sensor_attrs()`, and `occ_parse_poll_response()`.

Control flow: `occ_setup()` initializes the mutex, installs the status sysfs group, and optionally activates. Activation polls once, parses block headers, allocates a flat dynamic attribute array based on sensor versions/counts, and registers hwmon groups. Later sysfs reads call `occ_update_response()`, which polls at most once per second and otherwise reuses the last transport error. Power cap writes send command type `0x22`.

State and persistence: `struct occ` holds the last full response, parsed sensor pointers into that response, dynamic attributes, active flag, error counters, safe-state timestamp, and previous status values used by `sysfs.c`. Sensor topology is parsed once and assumed stable. Hardware power cap persists in OCC firmware.

Dependencies and integration: depends on the transport-provided `send_cmd`, hwmon sysfs helpers, common OCC response layout, jiffies, mutexes, unaligned big-endian access, and `occ_sysfs_poll_done()`.

Risks: parsed sensor data pointers point inside `occ->resp`, which is overwritten on every poll but layout is assumed unchanged. Dynamic attribute counts rely on known sensor versions; unsupported versions are hidden. Safe-state becomes fatal only after one minute. Error is promoted only after repeated transfer failures. The poll command checksum fields are zeroed and presumably handled by lower layers/OCC.

Test signals: activation with and without `ibm,no-poll-on-init`, each sensor version's attribute count and units, OCC safe-state timeout, repeated transfer error threshold, power cap writes, unsupported sensor block handling, response size validation, and hwmon unregister on deactivate/shutdown.

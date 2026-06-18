## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus.c

Purpose: implements the generic PMBus I2C driver used for devices that do not need a dedicated chip driver. It dynamically identifies page count, VOUT format, supported sensors, and status register availability, then delegates all runtime behavior to the PMBus core.

Important APIs, types, and functions: `struct pmbus_device_info` holds preset page count and platform flags. `pmbus_find_sensor_groups()` probes standard PMBus read/status registers and fills `info->func[]`. `pmbus_identify()` discovers pages, VOUT_MODE, rejects unsupported direct-mode coefficient handling, and calls sensor probing. `pmbus_probe()` allocates `pmbus_driver_info`, optional platform data, assigns `identify`, and calls `pmbus_do_probe()`.

Control flow: match data supplies one page, dynamic pages, or platform flags. If pages are unspecified, the driver tests PAGE support by setting successive pages up to the PMBus maximum. It clears faults, reads VOUT_MODE, sets voltage-out format for VID/direct/linear where possible, and probes standard telemetry groups before core registration.

State and persistence behavior: allocated `pmbus_driver_info` and optional platform data are devm-managed. Page detection changes the device PAGE register and clears faults. No per-device private state is retained outside PMBus core data.

Dependencies and integration points: uses `pmbus_check_*`, `pmbus_set_page()`, `pmbus_clear_faults()`, and `pmbus_do_probe()` from the core. The large I2C ID table maps many simple PMBus devices to generic handling and flags such as `PMBUS_SKIP_STATUS_CHECK`.

Risks and test signals: dynamic probing can perturb device fault state and may reject direct-mode devices that need coefficients. Test generic devices with/without PAGE, one-page skip/status flags, VID VOUT mode, and that unsupported direct coefficient cases fail with `-ENODEV` rather than exposing wrong units.

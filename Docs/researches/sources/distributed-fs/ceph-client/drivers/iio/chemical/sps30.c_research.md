# sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30.c

Purpose: shared IIO core for Sensirion SPS30 particulate matter sensors. Bus-specific I2C and serial files provide a `struct sps30_ops` table; this core owns IIO channels, measurement state, triggered-buffer support, fan-cleaning/sysfs controls, reset sequencing, and exported `sps30_probe()`.

Important APIs, types, and functions: `sps30_float_to_int_clamped()` converts big-endian IEEE754 non-negative PM values to fixed centi-units, clamped to the reliable 3000 ug/m3 limit. `sps30_do_meas()` lazily starts measurement after reset, calls `ops->read_meas()`, and converts requested float words. `sps30_do_reset()` calls transport reset and marks state `RESET`. `sps30_read_raw()` exposes processed PM1, PM2.5, PM4, and PM10 readings and shared scale. Sysfs attributes `start_cleaning`, `cleaning_period`, and `cleaning_period_available` call transport fan-cleaning and cleaning-period operations. `sps30_probe()` allocates the IIO device, initializes state and mutex, resets the chip, logs device info through the transport, registers stop-measure cleanup, sets up triggered buffer, and registers the device.

Control flow: direct PM reads request only enough measurement words for the target channel, while buffer capture always reads all four PM mass concentrations. Cleaning-period writes require a sensor reset before reads show the new value.

State and persistence: core state tracks only `RESET` versus `MEASURING`, mutex, device, transport private pointer, and ops. Cleaning period is persisted in sensor firmware, not cached by this core.

Dependencies and integration: depends on IIO buffer/triggered buffer, mutex, delays, and `sps30.h`. Exported in namespace `IIO_SPS30` for I2C and serdev transport modules.

Risks and test signals: lazy start means first measurement may pay setup cost and failures leave state reset. Float conversion assumes non-negative values and clamps high PM. Tests should cover all channel read lengths, trigger scan mask 0x0f, reset after cleaning-period write, fan-clean input validation, stop cleanup only when measuring, and transport error propagation.

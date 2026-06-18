<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_i2c.c

Purpose: I2C transport adapter for the Honeywell ABP2 common IIO core.

Important APIs, types, and functions: `abp2_i2c_read()` receives up to `ABP2_MEASUREMENT_RD_SIZE` bytes into the core RX buffer and validates exact length. `abp2_i2c_write()` writes the command byte plus requested byte count from the core TX buffer and validates exact length. `abp2_i2c_probe()` checks `I2C_FUNC_I2C` and calls `abp2_common_probe()` with the adapter ops and `client->irq`.

Control flow: probe binds compatible or I2C ID `abp2030pa`, creates no state of its own, and delegates all runtime behavior to the core. Direct and buffered reads later enter this file only through the ops table.

State and persistence: transport state is the I2C client embedded in `data->dev`; no separate private data or persistent state exists.

Dependencies and integration points: depends on the I2C subsystem, OF/I2C ID matching, and namespace import `IIO_HONEYWELL_ABP2030PA`. Integrates with the ABP2 core's buffer and command lengths.

Risks: write transfers send `nbytes` bytes even though only `tx_buf[0]` is explicitly set by this function; the common core currently requests three bytes for sync, so stale bytes can be transmitted unless the sensor ignores them as expected. No retries are performed on short transfers or NACKs.

Test signals: I2C functionality rejection, exact-length read/write checks, IRQ and no-IRQ probe paths, and logic-analyzer verification of sync/NOP packet sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_i2c.c -->

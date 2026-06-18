# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel.h

Purpose: private header shared by the STMicroelectronics accelerometer core, buffer helper, and I2C/SPI transport wrappers.

Important APIs/types/functions: declares the canonical device-name strings used by the settings table and bus match tables, including LIS3DH, LSM303 variants, LIS2DW12, LIS3DHH, SC7A20, and IIS328DQ. When `CONFIG_IIO_BUFFER` is enabled it declares `st_accel_allocate_ring()` and `st_accel_trig_set_state()` and maps `ST_ACCEL_TRIGGER_SET_STATE` to the trigger callback; otherwise it provides a no-op ring allocator and a NULL trigger callback.

Control flow: no runtime control flow exists in the header. Its conditional declarations determine whether the common probe can allocate a triggered buffer and expose a data-ready trigger callback.

State and persistence behavior: no state is stored. The names in this header are contract values used by bus modalias matching and `st_accel_get_settings()`.

Dependencies and integration points: includes `linux/iio/common/st_sensors.h` and is included by `st_accel_core.c`, `st_accel_buffer.c`, `st_accel_i2c.c`, and `st_accel_spi.c`.

Risks: device-name strings must stay synchronized with Kconfig/module aliases, OF/ACPI/I2C/SPI id tables, and the settings table. A mismatch causes probe to fail with "device name not recognized." The `CONFIG_IIO_BUFFER` stubs mean builds without buffer support still compile, but trigger-specific behavior silently disappears.

Test signals: compile both buffered and non-buffered configurations, verify all bus id-table names resolve through `st_accel_get_settings()`, and run modpost/export checks for `IIO_ST_SENSORS` namespace users.

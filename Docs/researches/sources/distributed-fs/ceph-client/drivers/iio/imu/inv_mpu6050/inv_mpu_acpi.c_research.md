# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_acpi.c

Purpose: ACPI helper for creating secondary I2C client devices behind the MPU I2C mux/gate, mainly for platform-specific auxiliary sensors.

Important APIs and functions: `inv_mpu_acpi_create_mux_client()` inspects ACPI/DMI state and creates an I2C client on `st->muxc->adapter[0]`; `inv_mpu_acpi_delete_mux_client()` unregisters it. Under `CONFIG_ACPI`, ASUS T100TA-specific parsing reads ACPI method `CNF0`; generic processing extracts primary/secondary addresses from ACPI I2C resources. Stub functions are provided when ACPI is disabled.

Control flow and state: the helper stores the created client in `st->mux_client`. It first tries DMI-specific parsing, then falls back to secondary-address extraction for INV6XX-style ACPI nodes. No client is created when no secondary address exists.

Dependencies and integration: Linux ACPI, DMI, I2C ACPI resource parsing, I2C mux created by `inv_mpu_i2c.c`, and shared `inv_mpu6050_state`.

Risks and tests: ACPI package parsing is platform-specific and must avoid creating a duplicate client for the primary MPU address. `i2c_unregister_device(NULL)` behavior depends on caller only invoking delete after setup. Test signals include ASUS T100TA probe, generic ACPI secondary address creation, no-client path, ACPI-disabled build, and remove path cleanup.

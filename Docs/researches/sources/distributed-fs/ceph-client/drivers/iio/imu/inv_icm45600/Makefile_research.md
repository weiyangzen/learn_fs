# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/Makefile

Purpose: maps ICM45600 Kconfig symbols to kernel objects.

Important rules: `inv-icm45600.o` is built when `CONFIG_INV_ICM45600` is selected and contains `inv_icm45600_core.o`, `buffer.o`, `gyro.o`, and `accel.o`. Transport modules are separate: `inv-icm45600-i2c.o`, `inv-icm45600-spi.o`, and `inv-icm45600-i3c.o`.

Control flow and state: build-only; no runtime state. The object split enforces one shared core module namespace and bus-specific entry modules.

Dependencies and integration: must stay aligned with Kconfig symbols and exported namespaces (`IIO_ICM45600`). The core exports chip-info tables and probe/PM symbols used by transport modules.

Risks and tests: omitted object files cause unresolved symbols or missing IIO functionality. Test signals include `make M=drivers/iio/imu/inv_icm45600`, modpost namespace checks, and verifying each transport module imports the shared namespace.

# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600.h

Purpose: central header for ICM45600-family state, chip descriptions, enums, register definitions, channel helpers, and cross-file prototypes.

Important types: `enum inv_icm45600_sensor_mode`, gyro/accel FSR enums, ODR enum, `struct inv_icm45600_sensor_conf`, shared `struct inv_icm45600_conf`, `struct inv_icm45600_chip_info`, global `struct inv_icm45600_state`, and per-child `struct inv_icm45600_sensor_state`. State includes lock, custom regmap, regulators, mount matrix, config cache, suspended modes, two IIO devices, chip info, interrupt timestamps, FIFO state, and DMA-aligned transfer buffer.

Important APIs: exported chip-info objects, scale tables, `inv_icm45600_core_probe()`, `inv_icm45600_set_accel_conf()`, `set_gyro_conf()`, temp read raw, debugfs, mount matrix, ODR-to-period, and child init/FIFO parse functions.

Integration: register definitions cover direct 8-bit registers and virtual 16-bit banked indirect registers. `INV_ICM45600_TEMP_CHAN()` defines little-endian temp scan slots. The header ties core, buffer, accel, gyro, and transport files together.

Risks and tests: ABI-sensitive channel macro and register constants must match datasheet endianness. State mutations rely on `st->lock`. Test signals include sparse/build checks, FIFO buffer layout validation, chip variant scale-table indexing, PM state restoration, and debugfs register access.

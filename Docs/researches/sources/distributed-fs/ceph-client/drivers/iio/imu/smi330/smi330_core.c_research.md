<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_core.c

Purpose: shared Bosch SMI330 IIO core. It defines register layout, channels, attributes, raw data/config sysfs, interrupt/trigger handling, device initialization, and the exported core probe used by I2C and SPI frontends.

Important APIs/types/functions: `struct smi330_data` owns regmap, operation/IRQ config, trigger, and aligned buffer. `smi330_regmap_config` exports 8-bit registers and 16-bit little-endian values. Important functions include `smi330_get/set_sensor_config()`, `smi330_get_data()`, `smi330_read_avail()`, `smi330_read_raw()`, `smi330_write_raw()`, `smi330_soft_reset()`, trigger and IRQ handlers, `smi330_register_irq()`, `smi330_set_drdy_trigger_state()`, `smi330_dev_init()`, and `smi330_core_probe()`.

Control flow: core probe soft-resets, initializes IIO metadata, validates chip/error/POR status, puts accel and gyro into normal mode, attempts named firmware IRQ lookup for `INT1` then `INT2`, optionally creates a data-ready trigger, sets it as the default trigger, installs a triggered buffer, and registers the IIO device. Raw reads claim direct mode and read signed 16-bit samples. Config writes map user values to register fields and check the error register for accel/gyro config errors. Data-ready trigger enable maps accel and gyro DRDY onto the selected interrupt pin; the threaded IRQ reads status and polls the nested trigger; the poll handler bulk reads six data registers and pushes a timestamped buffer.

State and persistence: `cfg.op_mode` records polling vs data-ready, `cfg.data_irq` records selected interrupt output, and hardware config registers persist ODR/range/bandwidth/averaging/mode. Buffer storage is per-device and aligned by IIO helper macros.

Dependencies and integration: uses regmap, fwnode named IRQs, irq trigger-type inspection, optional `drive-open-drain` firmware property, IIO triggered buffers, and bus frontends importing namespace `IIO_SMI330`.

Risks: unknown chip IDs are informational rather than fatal, while fatal error/POR checks are fatal. `smi330_read_raw()` assigns `*val` twice in the temperature scale path. `smi330_write_raw_get_fmt()` returns micro format for non-scale integer controls even though callers pass integers. IRQ setup requires supported trigger types and named `INT1`/`INT2`; without IRQ the device remains usable through direct/polled reads.

Test signals: probe on I2C/SPI, POR/fatal-error handling, raw temp/accel/gyro reads, available attribute lists, writes for range/ODR/BW/averaging including error-register rejection, named IRQ discovery, data-ready buffer capture, and open-drain/level/edge IRQ configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_core.c -->

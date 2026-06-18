<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_core.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_core.c

Purpose: shared IIO core for Honeywell HMC5843, HMC5883, HMC5883L, and HMC5983 magnetometers. It implements variant-specific channels, scale/frequency tables, measurement configuration enum, mount matrix, direct reads, triggered buffers, and sleep/resume handling.

Important APIs/types/functions: exported `hmc5843_common_probe()`, `hmc5843_common_remove()`, and `hmc5843_pm_ops` are consumed by bus wrappers. `struct hmc5843_chip_info` maps each variant to channels and scale/frequency tables. Main functions are `hmc5843_set_mode()`, `hmc5843_wait_measurement()`, `hmc5843_read_measurement()`, `hmc5843_set_meas_conf()`, raw read/write handlers, `hmc5843_trigger_handler()`, `hmc5843_init()`, and common PM callbacks.

Control flow: common probe allocates state, stores regmap/variant/mount matrix, configures IIO channels and scan masks, reads the 3-byte ID signature `H43`, sets normal measurement config, default sample rate and range gain, switches to continuous conversion, sets up triggered buffer, and registers the IIO device. Raw reads wait for data-ready then bulk-read three big-endian axes. Writes update sample-rate or range-gain bits after validating against variant tables. Triggered buffers use the same wait/read sequence and push the full scan.

State/persistence: chip mode, gain, rate, and measurement config live in device registers. Suspend sets sleep mode and resume restores continuous conversion, but other configuration remains in registers/regmap cache. Per-device orientation and variant pointer persist in memory.

Dependencies/integration: uses regmap supplied by I2C/SPI wrappers, IIO sysfs attributes, IIO enums/ext_info, triggered buffers, mount matrix, and module namespace `IIO_HMC5843`.

Risks: sample-rate and scale reads index tables directly from shifted register values without masking against table length, relying on valid hardware/config writes. `hmc5843_wait_measurement()` can block up to 150 * 20 ms. HMC5883/HMC5983 swap Y/Z channel ordering, which is ABI-visible. The core validates only the shared `H43` id bytes, not per-variant identity.

Test signals: test each variant id through I2C/SPI wrappers, scale/frequency read/write and availability files, measurement configuration enum including HMC5983 disabled mode, direct and buffered reads, Y/Z ordering, sleep/resume, and probe rejection when ID bytes differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_core.c -->

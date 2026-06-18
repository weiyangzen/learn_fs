# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_core.c

Purpose: shared IIO core for ADXL355 and ADXL359 low-noise 3-axis accelerometers. It implements ID/reset validation, raw acceleration and temperature reads, scale/offset/calibration bias, ODR and high-pass filter control, data-ready trigger support, and triggered buffers.

Important APIs/types/functions: exported symbols are `adxl355_readable_regs_tbl`, `adxl355_writeable_regs_tbl`, `adxl35x_chip_info[]`, and `adxl355_core_probe()`. Key internals are `adxl355_setup()`, `adxl355_set_op_mode()`, `adxl355_set_odr()`, `adxl355_set_hpf_3db()`, `adxl355_set_calibbias()`, `adxl355_read_raw()`, `adxl355_write_raw()`, `adxl355_probe_trigger()`, and `adxl355_trigger_handler()`.

Control flow: probe allocates IIO state, initializes standby mode and chip info, assigns channels and scan masks, runs setup, creates a triggered buffer, optionally registers a `DRDY` trigger, and registers the IIO device. Setup validates ADI/MEMS IDs, warns on unexpected part ID, snapshots shadow registers, repeatedly performs software reset until shadow registers match, disables data-ready output initially, computes HPF frequency table from ODR, and enters measurement mode. ODR/HPF/calibration writes switch to standby, update registers, then restore measurement.

State and persistence: `struct adxl355_data` stores chip info, regmap, device, mutex-protected op mode, ODR, HPF selection, cached calibration bias, computed HPF table, data-ready trigger, and DMA-aligned buffers. Hardware persists filter, offset, power, interrupt, and reset state.

Dependencies and integration: depends on regmap, IIO core, triggered buffer/trigger APIs, firmware IRQ named `DRDY`, unaligned big-endian access helpers, and bus frontends. It exports namespace `IIO_ADXL355`.

Risks: setup compares undocumented shadow registers after reset and can fail after five mismatches. Part-ID mismatch only warns, so wrong compatible data may still register with wrong scale. ODR/HPF/calibbias paths try to restore measurement after failures but preserve error returns. Trigger handler uses a shared buffer protected by the op-mode mutex.

Test signals: ID/reset success and shadow mismatch failure, raw 20-bit acceleration and temperature reads, scale/offset values for ADXL355 versus ADXL359, ODR and HPF available lists, calibration bias writes, DRDY-triggered buffer capture with timestamp, and operation without a DRDY IRQ.

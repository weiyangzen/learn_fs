<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.c

Purpose: common IIO core for Honeywell ABP2 pressure and temperature sensors. It is bus-neutral and is used by I2C and SPI front ends through `struct abp2_ops`.

Important APIs, types, and functions: `abp2_range_config[]` and `abp2_triplet_variants[]` map Honeywell pressure triplets to pascal ranges. `abp2_get_measurement()` sends a sync command, waits by IRQ or fixed sleep, reads a NOP packet, and validates the ABP2 status byte. `abp2_read_raw()` exposes pressure and temperature raw values plus IIO scale/offset. `abp2_trigger_handler()` pushes pressure and temperature scans. `abp2_common_probe()` allocates the IIO device, enables `vdd`, parses pressure properties, computes pressure scale/offset, optionally requests an EOC IRQ, sets up a triggered buffer, and registers the device.

Control flow: direct and buffered reads both call `abp2_get_measurement()`. Direct reads decode 24-bit pressure from bytes 1..3 and temperature from bytes 4..6. Probe accepts either `honeywell,pressure-triplet` or explicit `honeywell,pmin-pascal` and `honeywell,pmax-pascal`; function A is the only transfer function present.

State and persistence: all state is in `struct abp2_data`: pressure limits, output limits, computed scale and offset, IRQ/completion, DMA-aligned RX/TX buffers, and scan buffer. No nonvolatile state is modified. The driver remembers computed conversion parameters until removal.

Dependencies and integration points: depends on IIO buffers/triggers, regulator framework, firmware properties, completion/IRQ support, and bus callbacks from `abp2030pa_i2c.c` or `abp2030pa_spi.c`. It exports `abp2_common_probe` in namespace `IIO_HONEYWELL_ABP2030PA`.

Risks: no mutex protects direct reads versus triggered-buffer reads through shared `rx_buf`, `tx_buf`, and completion. `data->function` defaults to zero, so only function A is effectively supported and no property controls it. Status validation accepts only `ABP2_ST_POWER`; latch-up and all other status anomalies become hard I/O errors. `p_scale` arithmetic multiplies by `NANO` and should remain reviewed for 64-bit bounds as ranges evolve.

Test signals: property parsing for known triplets, explicit pmin/pmax fallback, invalid ranges, IRQ timeout, polling fallback, busy status, bad status bytes, I2C/SPI transport short-transfer faults, and buffered scan layout with both channels active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.c -->

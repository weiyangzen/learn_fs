# sources/distributed-fs/ceph-client/drivers/iio/gyro/adxrs290.c

## Purpose
SPI IIO driver for the dual-axis ADXRS290 gyroscope. It exposes X/Y angular velocity, temperature, low/high-pass filter controls, optional data-ready trigger, and triggered buffer capture.

## Important APIs, Types, And Functions
`struct adxrs290_state` stores SPI device, mutex, mode, cached filter indexes, trigger, and aligned scan buffer. Important functions include ID reads in probe, `adxrs290_set_mode`, `adxrs290_get_rate_data`, `adxrs290_get_temp_data`, filter get/set helpers, `adxrs290_read_raw`, `adxrs290_write_raw`, `adxrs290_read_avail`, debugfs reg access, trigger set/reenable callbacks, and `adxrs290_trigger_handler`.

## Control Flow
Probe validates ADI/MEMS/device IDs, switches to measurement mode with temperature sensor enabled, waits for transition, caches filter register values, sets up triggered buffer, optionally registers an IRQ-backed trigger, and registers the IIO device. Buffered reads bulk-read DATAX0 through temp into the scan buffer.

## State And Persistence
Hardware state includes power mode, temperature sensor enable, filter indexes, and data-ready output configuration. Software caches mode and filter indexes, so external debugfs writes can desynchronize sysfs-reported filter state.

## Dependencies And Integration Points
Depends on SPI, IIO buffers, triggered buffer, IIO triggers, optional device-tree `adi,adxrs290`, and an optional SPI IRQ for data-ready.

## Risks
Filter writes update cached indexes before the SPI write result is known, so failed writes can leave stale software state. Direct raw reads are guarded by `iio_device_claim_direct`; buffer users must handle `-EBUSY`. IRQ-free systems fall back to polling/no own trigger.

## Test Signals
Validate ID failure paths, read X/Y/temp raw and scale, enumerate available filter frequencies, write LPF/HPF legal and illegal values, run buffered capture with and without IRQ, and check standby cleanup on unbind.

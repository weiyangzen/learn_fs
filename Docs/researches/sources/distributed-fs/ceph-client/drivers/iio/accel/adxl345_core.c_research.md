# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_core.c

Purpose: shared IIO core for ADXL345 and ADXL375 accelerometers. It implements direct acceleration reads, scale/range and ODR control, calibration bias, activity/inactivity/free-fall events, single/double-tap events, FIFO buffering, interrupt handling, and common probe.

Important APIs/types/functions: exported functions are `adxl345_is_volatile_reg()` and `adxl345_core_probe()`. Key internal helpers include `adxl345_set_measure_en()`, ODR/range find/set helpers, activity/inactivity and tap config/value helpers, `adxl345_set_watermark()`, `adxl345_set_fifo()`, FIFO transfer/reset/push helpers, and `adxl345_irq_handler()`.

Control flow: core probe allocates IIO state, gets chip info from match data, seeds default tap and inactivity values, sets ODR to 200 Hz, range to 16g, disables interrupts, applies optional bus setup, enables full-resolution mode, validates device ID, enables measurement, installs a powerdown action, and either configures IRQ/FIFO/event defaults or FIFO bypass when no `INT1`/`INT2` IRQ is described. IRQ handling derives tap/activity axis direction, reads interrupt source, pushes IIO events, drains FIFO on watermark, and resets FIFO on errors/overrun.

State and persistence: `struct adxl345_state` stores chip info, regmap, SPI FIFO delay flag, watermark/FIFO mode, cached inactivity/tap parameters, and DMA-aligned FIFO buffer. Hardware registers persist offsets, thresholds, tap timing, range, ODR, interrupt routing, FIFO, and power state. A devm action disables measurement on teardown.

Dependencies and integration: depends on regmap, firmware IRQ properties, IIO core/events/kfifo buffers, units/bitfield helpers, and bus frontends. It exports namespace `IIO_ADXL345`.

Risks: `adxl345_write_raw()` disables measurement before validating all inputs and returns early on some errors without re-enabling measurement. Event enablement silently ignores invalid zero thresholds/timing. Range changes rescale thresholds and clamp to 1..255, which may surprise users. SPI FIFO delay is required above 1.5 MHz to satisfy FIFO pop timing.

Test signals: device ID rejection, scale/range and ODR sysfs lists, calibration bias, tap/double-tap timing constraints, activity/inactivity/free-fall events, FIFO watermark capture, overrun reset, no-IRQ bypass mode, and SPI high-speed FIFO reads.

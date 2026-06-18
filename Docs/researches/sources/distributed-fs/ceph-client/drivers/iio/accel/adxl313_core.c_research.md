# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_core.c

Purpose: shared IIO core for ADXL312/ADXL313/ADXL314 3-axis accelerometers. It implements register access policies, chip identity checks, raw acceleration, calibration bias, sampling frequency, activity/inactivity events, hardware FIFO buffering, interrupt handling, and common probe/setup.

Important APIs/types/functions: exported items are regmap access tables, `adxl313_is_volatile_reg()`, `adxl31x_chip_info[]`, and `adxl313_core_probe()`. Key internal functions include `adxl313_setup()`, `adxl313_read_raw()`, `adxl313_write_raw()`, event config/value helpers, `adxl313_set_watermark()`, FIFO setup/push/reset helpers, and `adxl313_irq_handler()`.

Control flow: core probe allocates an IIO device, initializes `adxl313_data`, sets channel/scan masks, performs optional soft reset and bus setup, checks IDs, configures full-resolution max range for variable-range chips, enables measurement, then either configures FIFO bypass when no `INT1`/`INT2` firmware IRQ exists or maps interrupts, seeds safe event defaults, sets up a kfifo buffer, and requests a threaded IRQ. IRQ handling reads `INT_SOURCE`, pushes activity/inactivity events, drains FIFO on watermark, and resets FIFO on unhandled/error conditions.

State and persistence: runtime state includes regmap cache, mutex, chip info, watermark, transfer buffer, and FIFO buffer. Device state persists in power control, data format, bandwidth, threshold, inactivity time, activity/inactivity control, interrupt map/enable, and FIFO registers.

Dependencies and integration: depends on regmap, firmware IRQ properties, IIO core/events/kfifo buffers, Linux bitfield helpers, and bus frontends. It exports namespace `IIO_ADXL313`.

Risks: event enable silently no-ops when thresholds or inactivity time are zero. Measurement is toggled around configuration; failure paths can leave measurement disabled in some intermediate register-write failures. `adxl313_set_watermark()` updates mode bits with the raw value before full FIFO stream setup, so FIFO register bit semantics must be preserved. Interrupt-less systems have no buffered capture path.

Test signals: ID warning paths, scale and ODR sysfs values, calibration bias bounds, activity/inactivity AC/DC events, watermark-triggered buffered reads, FIFO overrun recovery, and both INT1/INT2 firmware mappings.

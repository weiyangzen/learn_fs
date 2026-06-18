# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367.c

## Purpose

`adxl367.c` is the transport-independent IIO core for the Analog Devices ADXL367 low-power 3-axis accelerometer. It exposes accelerometer X/Y/Z channels, an internal temperature channel, an external ADC voltage channel, activity/inactivity threshold events, direct debug register access, and hardware FIFO buffered capture.

## Important APIs, Types, and Functions

The central state is `struct adxl367_state`, which keeps the regmap, transport `adxl367_ops`, device pointer, lock, selected ODR/range, cached activity thresholds and timers, FIFO set size/watermark, DMA-aligned FIFO/sample buffers, and small register write buffers. `adxl367_probe()` is the exported bus-facing entry point. Core configuration helpers include `adxl367_set_measure_en()`, `_adxl367_set_odr()`, `adxl367_set_range()`, threshold/time setters, FIFO mode/format/watermark setters, and temperature/ADC enable helpers.

The IIO surface is implemented by `adxl367_info`: `read_raw`, `write_raw`, `read_avail`, event config/value callbacks, `debugfs_reg_access`, `hwfifo_set_watermark`, and `update_scan_mode`. `adxl367_irq_handler()` reads status/FIFO count, pushes threshold events, and drains FIFO samples through the transport `read_fifo` callback.

## Control Flow

Probe allocates an IIO device, enables `vdd` and `vddio`, writes the reset code, waits for reset completion, validates the AD vendor ID, applies default setup, registers a kfifo buffer with hardware FIFO attributes, requests a threaded IRQ, and registers the IIO device. Setup programs default activity and inactivity thresholds, looped activity processing, 400 Hz ODR, activity/inactivity timers, then enters measurement mode.

Direct reads claim direct mode, optionally enable the temperature or ADC block, bulk-read a 16-bit sample, extract/sign-extend 14-bit data, and disable the auxiliary block again. Writes to scale or sampling frequency require direct mode and temporarily put the chip in standby because range/ODR changes affect active measurement behavior. Buffer enable configures the selected FIFO format from the active scan mask, enables auxiliary blocks when selected, enables FIFO watermark interrupts, switches FIFO to stream mode, and returns to measure mode; buffer disable reverses this sequence.

## State and Persistence Behavior

State is volatile and split between hardware registers and cached driver fields. The mutex protects driver fields and multi-register sequences. Range changes rescale cached activity thresholds and rewrite both thresholds. ODR changes rewrite activity and inactivity timer registers because timer periods depend on sample rate. FIFO watermark is cached as sample sets, while the hardware stores samples, so writes are converted through `fifo_set_size` and capped to the 511-sample hardware limit.

## Dependencies and Integration Points

The file depends on regmap, regulators, threaded IRQs, IIO core events, kfifo buffers, scan masks, sysfs FIFO attributes, and a small bus abstraction from `adxl367.h`. The actual FIFO read path is delegated to I2C/SPI wrappers because the command differs by transport.

## Risks

The standby/measure transitions are critical; early returns after disabling measurement may leave the device in standby if a later write fails. FIFO handling assumes valid scan masks and a nonzero `fifo_set_size`. `adxl367_push_fifo_data()` only drains when FIFO-full status is set, even though the interrupt is configured as watermark, so watermark semantics should be validated against hardware. Activity threshold/timer conversions silently clamp to hardware maxima. The typo-like enum name `ADCL367_ACT_REF_ENABLED` is harmless locally but easy to misread.

## Test Signals

Useful signals are successful regulator enable and device ID validation, sysfs raw/scale/offset/sample-frequency reads, rejection of invalid ODR/range values, event enable/value/period round-trips, FIFO watermark clamping, buffer enable for every advertised scan mask, IRQ delivery for activity/inactivity, FIFO sample ordering for X/Y/Z plus temp or ADC masks, and suspend-free unload with devm cleanup.

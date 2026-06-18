# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372.c

## Purpose

`adxl372.c` is the shared IIO core for ADXL371 and ADXL372 high-g accelerometers. It provides direct acceleration channels, activity/inactivity threshold events, configurable ODR and bandwidth, optional FIFO buffered capture, and IIO trigger integration.

## Important APIs, Types, and Functions

`struct adxl372_chip_info` is instantiated for ADXL371 and ADXL372 with sample-rate tables, bandwidth tables, timer scales, maximum ODR, and FIFO support. ADXL371 disables FIFO due to a documented silicon FIFO alignment erratum. `struct adxl372_state` stores chip info, IRQ, regmap, data-ready and peak triggers, FIFO mode/format/axis mask, ODR/bandwidth, event timers, interrupt bitmask, watermark, FIFO buffer, and threshold mutex.

Important functions include `adxl372_setup()`, `adxl372_set_op_mode()`, ODR/bandwidth setters, activity threshold/time setters, `adxl372_configure_fifo()`, `adxl372_trigger_handler()`, event callbacks, buffer setup, and exported `adxl372_probe()`.

## Control Flow

Probe allocates the IIO device, stores chip data, sets direct mode plus software buffer support only when FIFO is supported, runs setup, optionally creates triggered buffers and triggers, then registers the device. Setup verifies device ID, resets the chip, enters standby, programs default 1 g activity and 100 mg inactivity thresholds, looped activity mode, max ODR, 3200 Hz bandwidth, 1 ms activity and 10 s inactivity timers, then enters full-bandwidth measurement mode.

Runtime raw reads claim direct mode and read 16-bit axis registers. Sample frequency writes choose the closest supported ODR, recalculate timer registers, and constrain bandwidth to not exceed half the ODR. Buffer enable maps the active scan mask to FIFO format, handles peak FIFO mode, clamps watermark by set size, enables FIFO-full interrupts, configures FIFO in standby, and resumes measurement. The trigger handler reads status and FIFO count, pushes threshold events, drains FIFO when full, optionally rearranges peak samples, and notifies trigger completion.

## State and Persistence Behavior

The driver caches ODR, bandwidth, event durations, FIFO mode and watermark, and interrupt enable bits. Hardware timer registers are recomputed when ODR changes because timing scale depends on ODR and chip variant. Threshold writes use a dedicated mutex to serialize high/low byte updates. FIFO configuration always transitions through standby.

## Dependencies and Integration Points

The core depends on regmap, IIO triggered buffers, IIO triggers, event APIs, no-increment FIFO reads, and chip-info data supplied by I2C/SPI wrappers. `adxl372_readable_noinc_reg()` is exported so bus regmaps can mark FIFO data as a no-increment register.

## Risks

`adxl372_write_raw()` does not claim direct mode before changing ODR or bandwidth, so buffered operation interactions depend on higher-level IIO usage discipline. The data-ready trigger set-state only ORs the FIFO-full bit when enabling and does not clear it when disabling. FIFO drain subtracts one sample set before reading to avoid overwrite ordering issues; underflow must be avoided by the FIFO-full status and configured watermark. `adxl372_get_fifo_enabled()` prints enum value rather than boolean, which is user-visible but intentional-looking legacy behavior.

## Test Signals

Tests should cover ADXL371 vs ADXL372 chip-info binding, FIFO disabled for ADXL371, direct raw reads and scale, ODR/bandwidth availability and Nyquist truncation, event threshold/timer reads and writes, trigger allocation only with IRQ, peak FIFO trigger mode, watermark clamping, and FIFO drain ordering for one-, two-, and three-axis scan masks.

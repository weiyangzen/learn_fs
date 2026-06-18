# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7138.c

Purpose: I2C IIO driver for TI ADS7128/ADS7138 8-channel ADCs with auto sequencing, oversampling, sampling-frequency control, min/max/recent statistics, threshold events, and runtime PM conversion-mode switching.

Important APIs/types/functions: `struct ads7138_data` stores I2C client, `avdd` regulator, chip data, and a mutex for read-modify-write operations. Low-level helpers implement the device opcode protocol: block read/write, single write, set bit, and clear bit. IIO hooks are `ads7138_read_raw()`, `ads7138_write_raw()`, `ads7138_read_avail()`, event value/config accessors, `ads7138_event_handler()`, `ads7138_init_hw()`, and runtime suspend/resume callbacks.

Control flow: probe allocates IIO state, requests optional threaded IRQ, resets the chip, switches to auto mode, enables statistics and digital window comparator, enables all channels in auto sequence, starts sequencing, and registers IIO. Raw reads fetch the recent channel register pair; peak/trough read max/min registers. Writes program sampling frequency bits or OSR. Event configuration sets per-channel alert bits, and IRQ handling reads event flags, pushes rising/falling IIO events, then clears high/low flags.

State and persistence: conversion mode, OSR, sampling frequency, alert enables, thresholds, hysteresis, and statistics live in device registers. The driver keeps only the I2C client, regulator, chip metadata, and mutex in memory. Runtime PM changes conversion mode to manual/auto without persisting user settings.

Dependencies and integration: I2C, regulator framework, optional IRQ, IIO events, PM runtime macros, and OF/I2C IDs for `ti,ads7128` and `ti,ads7138`.

Risks: `indio_dev->num_channels` is always eight even though chip data has a channel count field; threshold value packing uses 12-bit threshold fields within two registers; event handler returns `IRQ_NONE` when no event flag is set, important for shared IRQs. Test signals include available frequency/OSR lists, threshold read/write boundaries, event IRQ push/clear behavior, runtime suspend/resume mode writes, and scale from `avdd`.

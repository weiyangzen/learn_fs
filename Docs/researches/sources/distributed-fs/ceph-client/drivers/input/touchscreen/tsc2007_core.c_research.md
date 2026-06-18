# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007_core.c

## Purpose
`tsc2007_core.c` is an I2C input driver for TI TSC2007-style resistive touch controllers. It samples raw X/Y/Z values, computes touch resistance, reports input events, supports legacy platform data, and optionally exposes raw channels through IIO.

## Important APIs, Types, And Functions
`tsc2007_xfer()` performs SMBus word reads and fixes the controller's byte/nibble ordering. `tsc2007_read_values()` sequences Y, X, Z1, Z2, then powers down with pen IRQ enabled. `tsc2007_calculate_resistance()` computes resistance from X/Z values and `x_plate_ohms`. `tsc2007_soft_irq()` loops while pen is down, filters pressure by `max_rt`, reports transformed coordinates, and sleeps for `poll_period`. Probe helpers parse firmware properties or `tsc2007_platform_data`.

## Control Flow
Probe checks SMBus word support, allocates state and input device, parses properties, registers optional platform cleanup, requests a threaded IRQ, powers the chip down, registers input, then calls `tsc2007_iio_configure()`. Open enables IRQ and prepares pen IRQ mode; close sets `stopped`, wakes the wait queue, and disables the IRQ. The IRQ thread serializes ADC accesses with `mlock`, reports down samples, and emits a final release.

## State And Persistence
Settings such as fuzz, max resistance, poll period, plate resistance, and touchscreen transform are parsed once and kept in memory. `stopped` controls the IRQ thread, while callbacks or GPIO provide pendown state. No persistent storage is used.

## Dependencies And Integration Points
It uses I2C SMBus, input core, touchscreen property parsing, optional GPIO descriptors, firmware properties, legacy platform data, wait queues, threaded IRQs, and optional IIO.

## Risks
Without a pendown GPIO/callback, release detection falls back to zero pressure and may be hardware-sensitive. The IRQ is requested before input registration and disabled through `tsc2007_stop()`, so enable/disable balance matters. IIO reads and IRQ sampling share the ADC and depend on `mlock` for serialization.

## Test Signals
Test property validation for `ti,x-plate-ohms`, GPIO pendown and no-GPIO modes, pressure filtering, open/close IRQ balancing, I2C error paths, platform callbacks, input transforms, IIO-enabled builds, and repeated suspend-like close/open cycles.

# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007_iio.c

## Purpose
`tsc2007_iio.c` adds an optional IIO direct-mode interface for TSC2007 raw ADC channels, touch resistance, pen state, and temperature inputs.

## Important APIs, Types, And Functions
`struct tsc2007_iio` links an IIO device to the existing `struct tsc2007`. `tsc2007_iio_channel[]` declares x, y, z1, z2, aux ADC, resistance, pen, temp0, and temp1 channels. `tsc2007_read_raw()` validates raw reads, serializes on `tsc->mlock`, issues the proper TSC2007 command sequence, computes resistance for channel 5, and powers down afterward. `tsc2007_iio_configure()` allocates and registers the IIO device with devm lifetime.

## Control Flow
The core calls `tsc2007_iio_configure()` after input registration. Each IIO read directly talks to the controller; it does not claim input device state, but it does take the ADC mutex shared with the input IRQ thread.

## State And Persistence
The IIO layer stores only a pointer to core state. It has no cache, no persistent settings, and reuses core calibration/resistance parameters.

## Dependencies And Integration Points
It depends on IIO direct mode, I2C command helpers from `tsc2007_core.c`, and the shared mutex in `struct tsc2007`.

## Risks
Individual `tsc2007_xfer()` errors are assigned into `*val` without a per-command negative return check, so failed reads can be reported as integer values. IIO reads can perturb pen IRQ power state, though the final `PWRDOWN` tries to restore it.

## Test Signals
Test all channel raw reads, invalid masks/channels, concurrent touch IRQ and IIO reads, I2C failure propagation expectations, and builds where the optional IIO config is disabled.

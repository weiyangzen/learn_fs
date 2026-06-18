# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d_spi.c

## Purpose
`lis3lv02d_spi.c` is the SPI glue layer for LIS302DL/LIS3 accelerometers. It configures SPI mode, provides byte read/write callbacks, passes IRQ/platform data to the shared core, and handles suspend/resume power transitions.

## Important APIs, types, and functions
Callbacks are `lis3_spi_read`, `lis3_spi_write`, and `lis3_spi_init`. Driver entry points are `lis302dl_spi_probe` and `lis302dl_spi_remove`. PM callbacks are `lis3lv02d_spi_suspend` and `lis3lv02d_spi_resume`. OF match supports `st,lis302dl-spi`.

## Control flow
Probe forces 8-bit words and SPI mode 0, calls `spi_setup`, fills the global `lis3_dev` with SPI callbacks, IRQ, normal axis mapping, and platform data, optionally parses OF data, stores driver data, and calls `lis3lv02d_init_device`. Remove disables joystick/freefall, powers off the sensor, and removes core sysfs. Suspend powers off unless platform wakeup flags require the sensor to remain armed; resume powers back on under the same condition.

## State and persistence
This transport stores its bus pointer and configuration in the global `lis3_dev`; it has no private allocation. Hardware register state is managed by the common core.

## Dependencies and integration points
The driver depends on SPI core helpers (`spi_w8r8`, `spi_write`, `spi_setup`), PM sleep ops, optional OF matching, platform data, and the shared LIS3 core.

## Risks
There is no block-read callback, so SPI reads use the slower per-register core path. The singleton core again prevents safe multi-device binding. Probe unconditionally changes `spi->mode`, which may surprise board descriptions if a variant needs a different mode. `lis3_spi_read` maps any negative SPI result to `-EINVAL`, losing the specific error code.

## Test signals
Tests should verify SPI setup parameters, read/write command bytes with the read bit, successful core initialization, IRQ/freefall behavior, OF parsing, suspend/resume with and without wakeup flags, and remove cleanup.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326_spi.c

## Purpose
`zpa2326_spi.c` is the SPI bus wrapper for Murata ZPA2326 sensors. It configures SPI register access and bus timing, then delegates core IIO behavior to `zpa2326_probe()`.

## Important APIs, types, and functions
`zpa2326_regmap_spi_config` defines 8-bit reg/val access, shared register validators, max register, and read flags for read plus address auto-increment (`BIT(7) | BIT(6)`). `zpa2326_probe_spi()` initializes regmap, forces SPI mode 3, caps speed at 1 MHz, runs `spi_setup()`, and calls the common probe with fixed `ZPA2326_DEVICE_ID`. Remove calls `zpa2326_remove()`.

## Control flow
The SPI core probes, regmap is created, SPI electrical settings are enforced, and the common core powers, validates, configures, and registers the IIO device. PM ops come from the shared core.

## State and persistence behavior
No wrapper-specific state persists beyond the SPI configuration and regmap. The common core owns all sensor runtime state.

## Dependencies and integration points
It depends on Linux SPI, regmap, OF/SPI ID matching for `murata,zpa2326`, and namespace `IIO_ZPA2326`.

## Risks
Forcing mode/speed can fail if controller constraints or firmware conflict. The read flag includes auto-increment, which is necessary for bulk pressure/temp reads but must be correct for single reads too. Remove assumes successful common driver-data setup.

## Test signals
Verify mode 3 and 1 MHz cap, regmap reads/writes including bulk reads, probe ID mismatch, PM paths, and common one-shot/triggered-buffer behavior over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326_spi.c -->

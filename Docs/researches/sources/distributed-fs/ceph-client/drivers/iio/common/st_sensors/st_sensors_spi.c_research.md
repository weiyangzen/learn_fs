
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_spi.c

## Purpose
`st_sensors_spi.c` provides common SPI setup for ST IIO sensor drivers. It handles optional 3-wire SPI configuration, initializes an 8-bit register/8-bit value regmap with optional multi-read flag, and records SPI device identity/IRQ into IIO state.

## Important APIs, types, and functions
- `ST_SENSORS_SPI_MULTIREAD` is the `0xc0` read flag used when sensor metadata requires a multi-read bit.
- `st_sensors_is_spi_3_wire()` checks firmware property `spi-3wire` or legacy platform data.
- `st_sensors_configure_spi_3_wire()` writes the sensor SIM register when provided in settings.
- `st_sensors_spi_configure()` performs 3-wire setup, creates SPI regmap, binds driver data, names the IIO device, and stores the IRQ.
- The configure helper is exported in namespace `IIO_ST_SENSORS`.

## Control flow
Sensor-specific SPI probes call this after selecting `sensor_settings`. If 3-wire mode is requested and supported by settings, a two-byte SPI write configures the SIM register before regmap creation. The helper then chooses the regmap config based on `multi_read_bit`, initializes regmap, and records bus metadata.

## State and persistence behavior
The file may persistently change the sensor's SIM register for 3-wire mode. Runtime state set in memory includes `sdata->regmap`, `sdata->irq`, `indio_dev->name`, and SPI driver data.

## Dependencies and integration points
It depends on SPI core, property APIs, regmap SPI, IIO core, ST platform data, and public `linux/iio/common/st_sensors_spi.h`. `st_sensors_core.c` uses the configured regmap for all later sensor operations.

## Risks and edge cases
- If 3-wire is requested but `settings->sim.addr` is zero, the helper silently does nothing; that may be correct for devices auto-configured by wiring, but it can also mask unsupported 3-wire requests.
- Incorrect `multi_read_bit` metadata changes every bulk read protocol.
- The pre-regmap raw `spi_write()` for SIM setup bypasses regmap locking/cache behavior, which is appropriate at probe but should remain early-only.

## Test signals
Probe with firmware `spi-3wire`, legacy `spi_3wire`, and normal SPI configurations. Confirm SIM writes occur when expected, regmap uses `0xc0` read flag for multi-read devices, and IRQ/name fields are populated.

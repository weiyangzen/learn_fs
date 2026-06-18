# sources/distributed-fs/ceph-client/drivers/iio/gyro/adxrs450.c

## Purpose
SPI IIO driver for ADXRS450/ADXRS453 digital-output gyroscopes, exposing Z angular velocity, temperature, quadrature correction, and optional calibration bias depending on variant.

## Important APIs, Types, And Functions
`struct adxrs450_state` holds SPI device, mutex, and aligned 32-bit TX/RX buffers. Key helpers are `adxrs450_spi_read_reg_16`, `adxrs450_spi_write_reg_16`, `adxrs450_spi_sensor_data`, `adxrs450_spi_initial`, `adxrs450_initial_setup`, `adxrs450_read_raw`, and `adxrs450_write_raw`.

## Control Flow
Probe allocates/registers the IIO device and then runs the datasheet startup handshake. The initial setup waits, issues check and no-check sensor-data commands, validates status bits, then reads fault registers. Register reads use a two-transfer SPI sequence with parity generation.

## State And Persistence
Hardware state is mostly read-only sensor data plus dynamic-null correction writes for ADXRS450 calibration bias. The driver has no runtime PM or cleanup power-down path. Software state is limited to protected SPI buffers.

## Dependencies And Integration Points
Depends on SPI and IIO direct mode. Supports SPI IDs `adxrs450` and `adxrs453` with variant-specific channel masks.

## Risks
Probe registers the IIO device before initial hardware setup, so a later startup failure leaves error flow reliant on devm cleanup after a short registration window. Startup response checks are strict and timing-sensitive. The source includes an apparent duplicate `return ret;` in setup.

## Test Signals
Probe both IDs, verify startup fault/status handling, read angular velocity and temperature raw/scale, read quadrature correction, write calibration bias on ADXRS450 and confirm ADXRS453 rejects it, and run SPI parity/fault injection if available.

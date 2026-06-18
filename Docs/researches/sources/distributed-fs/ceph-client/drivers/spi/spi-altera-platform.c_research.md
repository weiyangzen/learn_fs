# sources/distributed-fs/ceph-client/drivers/spi/spi-altera-platform.c

## Purpose

`spi-altera-platform.c` is the platform-bus wrapper for the shared Altera SPI core. It handles platform data, OF matching, MMIO regmap setup, optional IRQ registration, and legacy board-info child creation.

## Important APIs, types, and functions

- `enum altera_spi_type` distinguishes normal MMIO controllers from `subdev_spi_altera` instances using a parent regmap and register offset.
- `spi_altera_config` describes the 32-bit MMIO regmap.
- `altera_spi_probe()` allocates and configures the SPI controller, maps or locates its regmap, initializes the shared core, requests an optional IRQ, registers the controller, and creates board-info devices from platform data.
- OF match table supports `ALTR,spi-1.0` and `altr,spi-1.0`.

## Control flow

Probe chooses host parameters from `struct altera_spi_platform_data` when present, otherwise defaults to 16 chipselects, `SPI_CS_HIGH`, and 1-16 bits per word. For subdevices it retrieves the parent regmap and optional register offset; for normal platform devices it maps MMIO and creates a regmap. It then calls `altera_spi_init_host()`, optionally requests `altera_spi_irq()`, registers the controller, and instantiates platform-data child devices.

## State and persistence behavior

State lives in the SPI controller and `struct altera_spi` private data. The wrapper uses non-devm `spi_alloc_host()` and calls `spi_controller_put()` on probe failure; successful registration is device-managed. Register state is initialized by the shared core and persists until transfers or device removal.

## Dependencies and integration points

The wrapper integrates with platform devices, device tree, legacy platform data, regmap-mmio, optional IRQs, and the exported Altera core. It consumes `struct altera_spi_platform_data` from `linux/spi/altera.h`.

## Risks and edge cases

- The IRQ is optional; missing or negative IRQs put the shared core into polling mode.
- Subdevice mode requires the parent to expose a regmap; otherwise probe fails.
- Platform-data device creation failures are warnings, not probe failures.
- Default chipselect and bits-per-word masks must match actual synthesized hardware when no platform data is supplied.

## Test signals

Build with `CONFIG_SPI_ALTERA`. Runtime tests should cover OF and platform-data probing, normal MMIO and subdevice regmap paths, IRQ and polling transfer modes, invalid `num_chipselect`, and child-device creation.

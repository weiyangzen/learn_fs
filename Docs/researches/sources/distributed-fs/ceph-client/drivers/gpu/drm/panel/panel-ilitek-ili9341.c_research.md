# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9341.c

## Purpose

This SPI/DBI controlled DRM panel driver supports an Ilitek ILI9341 panel in DPI/RGB mode, currently the `st,sf-tc240t-9370-t` panel on the STM32F429 Discovery board. SPI is used for command setup through MIPI DBI while pixel data is supplied over a DPI RGB interface.

## Important APIs, Types, And Functions

`struct ili9341_config` stores the fixed mode and all controller register payloads needed for power, timing, VCOM, address mode, RGB interface, pixel format, and gamma setup. `struct ili9341` stores config, panel, reset/data-command GPIOs, `mipi_dbi`, SPI speed, and regulators.

`ili9341_dpi_init()` sends the register program using `mipi_dbi_command()` and `mipi_dbi_command_stackbuf()`. `ili9341_dpi_power_on()` and `ili9341_dpi_power_off()` control reset and regulators. DRM panel funcs implement prepare, enable, disable, unprepare, and get-modes. `ili9341_probe()` gets reset and D/C GPIOs and delegates to `ili9341_dpi_probe()`.

## Control Flow

Probe obtains GPIOs, allocates a DPI connector panel, allocates a DBI context, gets supplies `vci`, `vddi`, and `vddi-led`, initializes SPI DBI, loads match config, and registers the panel. Prepare powers the panel and sends the full initialization table, including sleep-out and display-on. Enable sends display-on again. Disable sends display-off. Unprepare asserts reset and disables supplies.

## State And Persistence

All configuration is static match data. Runtime state is limited to GPIO, regulator, DBI, and panel registration state. There is no persistent storage or runtime mode switching.

## Dependencies And Integration Points

The driver depends on SPI, MIPI DBI helpers, DRM panel, DRM bus flags, GPIO, regulator bulk APIs, and OF/SPI device IDs. It exposes a DPI connector and communicates control commands over SPI using a D/C GPIO.

## Risks

Only one board-specific config is present; adding panels means adding a full register table. `max_spi_speed` is stored but not visibly applied to `spi->max_speed_hz` in this file. `ili9341_dpi_prepare()` does not check command return values from the init sequence, so DBI command failures may not abort prepare. The init sequence includes long fixed sleeps and repeated display-on/write-memory-start commands that are hardware-specific.

## Test Signals

Validate SPI DBI initialization, GPIO acquisition, regulator enable order, expected 240x320 mode with correct bus flags and sync flags, visible RGB scanout after prepare, DBI command traces during initialization, and clean display-off/reset/power-off during unprepare.

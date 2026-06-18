# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-spi.c

## Purpose

This is the SPI/MIPI DBI transport driver for ILI9806E panels using the shared core. It supports the Rocktech RK050HR345-CT106A panel as a DPI connector with SPI command initialization.

## Important APIs, Types, And Functions

`struct ili9806e_spi_panel` stores the SPI device, embedded `mipi_dbi`, and descriptor. `struct ili9806e_spi_panel_desc` stores a fixed mode, media bus format, bus flags, and init callback.

`ili9806e_spi_prepare()` powers on through the core and runs the descriptor init sequence. `ili9806e_spi_unprepare()` sends display-off/sleep-in via DBI and powers off. `ili9806e_spi_get_modes()` duplicates the fixed mode and fills connector physical size, bus flags, and bus format. `ili9806e_spi_probe()` initializes DBI over SPI and calls the shared core probe with a DPI connector type.

## Control Flow

Probe allocates transport state, stores SPI and descriptor pointers, initializes MIPI DBI without a D/C GPIO argument, and delegates common panel setup to the core. Prepare powers on, sends page-based DBI commands for interface, power, timing, gamma, GIP, address mode, sleep-out, waits, and display-on. Unprepare sends display-off and sleep-in before core power-off. Remove only removes the core panel because there is no DSI host detach.

## State And Persistence

There is no persistence. Runtime state is the DBI context, SPI device, descriptor, and core-owned power/backlight resources. Bus format and bus flags are descriptor constants exposed during mode query.

## Dependencies And Integration Points

The driver depends on SPI, MIPI DBI helpers, DRM panel, media bus formats, the shared ILI9806E core, and OF/SPI IDs. It exposes compatible `rocktech,rk050hr345-ct106a` and SPI ID `rk050hr345-ct106a`.

## Risks

DBI command helpers used in the init and off paths do not propagate errors here, so prepare can return success despite failed SPI commands. The core power-off return is logged but `ili9806e_spi_unprepare()` returns zero. The DBI init call has no D/C GPIO, so it depends on the SPI wiring/protocol supported by `mipi_dbi_spi_init()`. Any new panel requires careful bus format and bus flag selection, since these affect the upstream display controller.

## Test Signals

Validate SPI DBI initialization, core regulator/reset/backlight setup, 480x854 mode and RGB888 bus format reporting, display-on after the init sequence, command traces for sleep-out/display-on, and suspend/resume behavior where DBI off and core power-off both execute.

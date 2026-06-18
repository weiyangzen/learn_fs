# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7789v.c

## Purpose
This SPI-based DRM panel driver supports ST7789V-compatible LCD controllers attached as DPI panels controlled over 9-bit SPI. It programs controller timing, RGB interface polarity, gamma/power settings, optional inversion, and optional partial-mode row limits.

## Important APIs, Types, And Functions
`struct st7789_panel_info` describes the fixed mode, bus format, bus flags, inversion, and partial mode window. `struct st7789v` holds the DRM panel, selected panel info, SPI device, optional reset GPIO, power regulator, and orientation. SPI access is implemented by `st7789v_spi_write()`, `st7789v_write_command()`, `st7789v_write_data()`, and `st7789v_read_data()`. `st7789v_check_id()` optionally verifies display ID when RX is available.

Panel operations are `st7789v_prepare()`, `st7789v_enable()`, `st7789v_disable()`, `st7789v_unprepare()`, `st7789v_get_modes()`, and `st7789v_get_orientation()`. Probe configures 9-bit SPI and binds regulator, reset, backlight, and orientation.

## Control Flow
Probe allocates the panel, sets `spi->bits_per_word = 9`, runs `spi_setup()`, fetches match data, gets `power`, reset GPIO, OF backlight, and orientation, then adds the panel. Prepare derives pixel format and polarity from `info->bus_format`, display mode flags, and bus flags. It enables the regulator, toggles reset, optionally checks the display ID, exits sleep, waits 120 ms, programs address mode, pixel format, porch/gate/VCOM/power/gamma/RGB control registers, handles inversion, and optionally enters partial mode with configured row bounds. Enable sends display-on. Disable sends display-off. Unprepare sends sleep-in and disables the regulator.

## State And Persistence
The driver stores only static panel info and runtime hardware handles. There is no nonvolatile state. Orientation and display info are reported through connector state. The controller is fully reprogrammed on each prepare.

## Dependencies And Integration Points
It uses DRM panel and connector APIs, SPI, regulator, GPIO, MIPI DCS command definitions, media bus formats, bus flags, OF/SPI match tables, OF backlight, and orientation helpers. It exposes SPI IDs and OF compatibles for several panels.

## Risks
`st7789v_read_data()` implements unusual 9-bit read packing; ID reads are skipped on `SPI_NO_RX` and only warn on mismatch in prepare, so a wrong panel can still proceed. Bus format support is limited to RGB666 and RGB565; unsupported descriptors fail prepare. Partial mode assumes userspace uses the advertised mode, as noted in the source comment. Several ST7789V register settings are fixed rather than per-panel, which can be a problem for new compatibles.

## Test Signals
Check `spi_setup()` with 9-bit transfers, regulator/reset timing, optional ID warning behavior, fixed mode and bus format propagation, inversion/partial-mode behavior, and display recovery after disable/unprepare. For new panel info, test both RX-capable and no-RX SPI configurations.

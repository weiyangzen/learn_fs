# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-tpg110.c

## Purpose
This SPI/DPI driver supports the TPO TPG110 LCD controller. Because the chip drives several possible LCD resolutions, the driver detects the configured resolution over SPI, maps it to a supported DRM mode, reads physical dimensions from device tree, and toggles standby through controller registers.

## Important APIs, Types, And Functions
`struct tpg110_panel_mode` maps controller magic values to mode names, `drm_display_mode`, and bus flags. `struct tpg110` stores device/SPI/panel handles, detected panel mode, width/height, and reset GPIO `grestb`. SPI access is in `tpg110_readwrite_reg()`, with `tpg110_read_reg()` and `tpg110_write_reg()` wrappers.

`tpg110_startup()` deasserts reset, performs a communication test, logs chip ID and resolution, maps dual-scan variants to producer-side modes, selects the panel mode, and takes software control of resolution/standby. Panel ops are enable, disable, and get_modes.

## Control Flow
Probe allocates the panel, reads `width-mm` and `height-mm`, gets reset GPIO initially asserted, configures SPI for 8-bit 3-wire high-impedance mode, stores the SPI device, runs startup detection, binds optional OF backlight, sets driver data, and adds the panel. Enable reads the power-management control bit and sets it. Disable reads the same register and clears it. Get-modes duplicates the detected mode and sets connector dimensions and bus flags.

## State And Persistence
Detected panel mode and dimensions are kept for the device lifetime. The controller remains configured for software control after startup. There is no persistent software storage.

## Dependencies And Integration Points
The driver depends on DRM panel, SPI 3-wire Hi-Z support, GPIO reset, OF properties for dimensions, OF/SPI match tables, and OF backlight. It exposes a DPI connector.

## Risks
The code logs missing width/height properties but does not fail, so zero dimensions can be reported. SPI read/write returns `u8`, so negative `spi_sync()` errors are truncated when returned from `tpg110_readwrite_reg()`, which can hide failures in callers expecting register values. `tpg110_disable()` and `tpg110_enable()` use `TPG110_CTRL2_PM` as the register address even though it is a bit definition, which deserves careful audit against the datasheet. Unsupported hardware-configured resolutions fail probe.

## Test Signals
Test SPI communication test failure, all supported resolution magic values, width/height property handling, standby enable/disable, backlight binding, and real bus flag behavior. Static tests should flag the bit-vs-register ambiguity in enable/disable.

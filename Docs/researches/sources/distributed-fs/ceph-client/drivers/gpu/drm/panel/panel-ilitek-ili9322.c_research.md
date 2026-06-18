# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9322.c

## Purpose

This SPI-controlled DRM panel driver supports Ilitek ILI9322 TFT LCD controllers, including the D-Link DIR-685 panel. The controller accepts multiple input formats, including serial RGB, parallel RGB, YUV, and BT.656; the driver chooses a DRM mode according to the configured or probed input mode.

## Important APIs, Types, And Functions

`struct ili9322_config` describes board-specific physical size, flips, input format, voltage settings, sync polarity/mode, and gamma correction. `struct ili9322` stores the device, config, DRM panel, regmap, supplies, reset GPIO, selected input, gamma and voltage register values.

SPI register access is abstracted through `ili9322_regmap_spi_write()` and `ili9322_regmap_spi_read()` with bit 7 selecting read versus write. `ili9322_init()` resets the controller, applies voltage/gamma/polarity/interface/input registers, and logs the selected input mode. `ili9322_get_modes()` chooses the DRM mode and bus flags for the selected input. `ili9322_probe()` validates board config, derives register encodings, enables regmap, reads the chip ID, optionally probes the entry register, and registers the panel.

## Control Flow

Probe is SPI-only and creates a DPI connector panel. It requires OF match data with a board configuration; the generic `ilitek,ili9322` match has NULL data and intentionally fails as missing configuration. It configures regulators and voltage constraints, optional reset GPIO, SPI 8-bit mode, regmap, and chip ID. Prepare powers regulators, releases reset, then initializes registers. Enable writes power-control normal mode; disable writes standby; unprepare disables supplies.

## State And Persistence

No state is persisted. Runtime state includes selected input mode, derived voltage register values, gamma table, and regmap cache. The regmap uses `REGCACHE_MAPLE`, but the driver performs explicit initialization during prepare and does not rely on persistent hardware state.

## Dependencies And Integration Points

The driver depends on SPI, regmap, regulator bulk APIs, GPIO, DRM panel, video mode definitions, and device-tree match data. Board integration must provide a concrete `ili9322_config`, supplies `vcc`, `iovcc`, `vci`, and optional reset GPIO. It exposes a DPI connector because pixel data enters through an external RGB/YUV/BT.656 path, not through SPI.

## Risks

Board configuration is mandatory and highly hardware-specific; bad voltage or gamma values can produce electrical or display-quality issues. The conversion for `vcom_amplitude_percent == 0` assigns `ili->vcom_high = U8_MAX` instead of `ili->vcom_amplitude`, which looks suspicious and can leave `vcom_amplitude` uninitialized unless config supplies it. Probe rejects missing chip ID, so boards with inaccessible ID wiring will not bind. Mode selection depends on input encoding and only covers known input modes.

## Test Signals

Check SPI regmap read of chip ID `0x96`, regulator voltage setup, correct input-mode log, expected connector mode for the configured input, bus flags matching polarity properties, register writes during prepare, standby/normal power-control writes during disable/enable, and visual validation of scaling for YUV/BT.656 modes.

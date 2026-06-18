# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-innolux-ej030na.c

## Purpose

This is an SPI-controlled DRM panel driver for the Innolux/Chimei EJ030NA TFT LCD panel. The panel uses SPI register programming for control and a DPI connector for pixel data.

## Important APIs, Types, And Functions

- `struct ej030na_info` describes modes, physical size, media bus format, and bus flags.
- `struct ej030na` stores the DRM panel, SPI device, regmap, matched panel info, power regulator, and reset GPIO.
- `ej030na_init_sequence` is the static register table written during prepare.
- `ej030na_prepare()` enables power, pulses reset, and writes the init sequence through regmap.
- `ej030na_enable()` and `ej030na_disable()` control standby through register `0x2b`.
- `ej030na_get_modes()` publishes two 320x480 modes and sets bus format/flags.
- `ej030na_probe()` allocates a DPI panel, initializes SPI regmap, gets resources/backlight, and adds the panel.

## Control Flow

The SPI driver matches `innolux,ej030na`. Probe creates an 8-bit register/8-bit value regmap and stores static match data. Prepare powers and initializes the panel. Enable exits standby and waits 120 ms before backlight use. Disable enters standby. Removal unregisters, disables, and unprepares the panel.

## State And Persistence

The driver keeps only volatile kernel state. Hardware register state is reloaded on every prepare. There is no EDID, persistent brightness storage, or dynamic mode detection.

## Dependencies And Integration Points

Integration points are SPI, regmap, regulator, reset GPIO, DRM panel, optional OF backlight, media bus format definitions, and DPI connector bus flags. The display controller must honor RGB888 delta format and DE/pixel-clock polarity.

## Risks

`ej030na_enable()` and `ej030na_disable()` ignore `regmap_write()` errors. Incorrect bus flags or timing values can cause shifted image, wrong colors, or missing sync. Two modes are exposed without marking a preferred mode, leaving selection to userspace policy.

## Test Signals

Check SPI probe, regmap initialization, regulator/reset acquisition, full init write success, standby writes, both 320x480 modes, RGB bus polarity, color correctness, and frame stability at both refresh rates.

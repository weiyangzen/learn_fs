# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_ams_delta.c

## Purpose
`lcd_ams_delta.c` provides the legacy OMAP framebuffer panel description and LCD class hooks for the Amstrad E3/Delta videophone panel.

## Important APIs, Types, And Functions
- `ams_delta_panel` is the `struct lcd_panel` registered with omapfb. It defines a 480x320, 12-bpp, 16-data-line STN-style panel with timing fields and GPIO enable/disable callbacks.
- `ams_delta_lcd_set_power()` and `ams_delta_lcd_set_contrast()` manipulate OMAP PWL registers for LCD power/contrast.
- When `CONFIG_LCD_CLASS_DEVICE` is enabled, `ams_delta_lcd_ops` exposes power and contrast via the LCD class.
- `ams_delta_panel_probe()` acquires `vblen` and `ndisp` GPIOs, optionally registers an LCD class device, initializes contrast and power, then registers the panel.

## Control Flow
The platform driver probe obtains two GPIO descriptors, registers the optional LCD class device, writes default contrast and power-on state to the PWL hardware, and calls `omapfb_register_panel()`. Panel enable asserts NDISP and VBLEN; disable deasserts them in reverse order.

## State And Persistence
Static `ams_delta_lcd` stores current contrast in the low byte and a power flag in bit `AMS_DELTA_LCD_POWER`. GPIO descriptors are global static pointers. No state persists across reboot or module unload.

## Dependencies And Integration Points
The file depends on OMAP1 PWL register access through `omap_writeb()`, gpiod descriptors, the LCD class, and the legacy `omapfb_register_panel()` handshake. The timing fields are consumed by `lcdc.c` during controller setup.

## Risks
Power and contrast state are global and not protected by a lock. `ams_delta_lcd_set_contrast()` silently ignores out-of-range values but still returns success. There is no remove path to unregister the optional LCD class device. Hardware register writes assume OMAP1 Delta-specific PWL semantics.

## Test Signals
Probe should register an `omapfb` LCD class device when configured, expose contrast/power controls, and produce visible panel enable/disable behavior through the VBLEN/NDISP GPIOs.

# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_mipid.c

## Purpose
`lcd_mipid.c` is a SPI-driven panel driver for MIPI DBI-C/DCS-compatible LCDs in the legacy OMAP fbdev stack. It detects supported panels, registers a `struct lcd_panel`, controls sleep/display/backlight state, performs ESD checks for LS041Y3, and supports a framebuffer-to-panel RGB interface test.

## Important APIs, Types, And Functions
- `struct mipid_device` stores SPI device, reset GPIO, embedded `lcd_panel`, fbdev pointer, guard timing, enabled state, saved backlight level, and delayed ESD work.
- `mipid_transfer()` builds 9-bit SPI command/data/read transactions.
- DCS helpers `mipid_cmd()`, `mipid_write()`, and `mipid_read()` wrap panel access.
- Power/display flow uses `set_sleep_mode()`, `set_display_state()`, `mipid_enable()`, and `mipid_disable()`.
- Backlight methods forward to `struct mipid_platform_data` callbacks.
- `mipid_run_test()` writes the first fb pixel through omapfb and reads panel RGB registers.
- `mipid_detect()` reads display ID and selects `lph8923` or `ls041y3`; `mipid_spi_probe()` allocates, requests reset GPIO, detects, and registers the panel.

## Control Flow
Probe allocates `mipid_device`, deasserts reset through the reset GPIO, sets SPI mode, copies default panel timings, detects the panel over DCS, then calls `omapfb_register_panel()`. During omapfb panel initialization, `mipid_init()` records the fbdev, initializes work and mutexes, reads whether the bootloader already enabled the panel, and starts ESD monitoring or saves current brightness. Enable exits sleep, sends init commands and data-line format, turns display on, restores brightness, and starts ESD checks. Disable cancels ESD work, saves brightness, turns backlight/display off, enters sleep, and marks disabled.

## State And Persistence
Runtime state is per SPI device. `hw_guard_end` and `hw_guard_wait` enforce DCS sleep-in/out spacing. `saved_bklight_level` preserves desired brightness while disabled. Delayed work periodically performs ESD validation only while enabled. No persistent storage is used.

## Dependencies And Integration Points
The driver depends on SPI, GPIO descriptors, platform data from `linux/platform_data/lcd-mipid.h`, delayed work, and legacy omapfb panel registration. It calls `omapfb_write_first_pixel()` for diagnostics and uses panel timing fields consumed by `lcdc.c`.

## Risks
`mipid_spi_probe()` leaks the allocated `mipid_device` if reset GPIO acquisition fails because it returns directly. SPI transfer read handling assumes panel-specific 9-bit protocol quirks. Backlight platform callbacks are optional but not consistently checked by all call paths. ESD recovery performs sleep transitions under the mutex and may disturb active updates. `set_data_lines()` has no default error path before writing `par`.

## Test Signals
Expected signals include successful display ID log, correct panel name/revision/data-line reporting, sleep/display/backlight transitions, stable delayed ESD work, and a passing `MIPID_TEST_RGB_LINES` test that writes and reads known first-pixel values.

# sources/distributed-fs/ceph-client/drivers/video/backlight/hp680_bl.c

## Purpose
This legacy platform driver controls HP Jornada 680 LCD backlight brightness using SH DAC output and HD64461 GPIO bits.

## Important APIs, Types, and Functions
File-scope state includes `hp680bl_suspended`, `current_intensity`, and `bl_lock`. `hp680bl_send_intensity()` computes effective brightness, serializes hardware access with a spinlock, enables or disables the DAC, toggles the LCD-off bit, and outputs inverted intensity through `sh_dac_output()`. Backlight callbacks wrap this helper, and PM callbacks force zero on suspend and restore on resume.

## Control Flow
Module init manually registers both the platform driver and a simple platform device named `hp680-bl`. Probe registers a raw backlight with max 255 and default 10, stores the backlight device as driver data, and applies brightness. Remove sets brightness to zero and calls the hardware path. Exit unregisters device and driver.

## State and Persistence
State is global and assumes one HP680 backlight. `current_intensity` is volatile. The hardware DAC/GPIO state persists only until the platform reinitializes it.

## Dependencies and Integration Points
The driver depends on SuperH/Jornada platform headers, `sh_dac_*`, HD64461 port accessors, platform devices, and the backlight subsystem. It is tightly bound to the HP680 board and not firmware-described.

## Risks
The driver uses direct port I/O and global state, so it is not suitable for multiple devices. Brightness is inverted for DAC output (`255 - intensity`), so polarity mistakes produce reversed brightness. PM state and current intensity are not protected by a separate mutex, though hardware writes are spinlocked.

## Test Signals
Test module init/exit, default brightness programming, zero/nonzero transitions, DAC enable/disable, HD64461 LCDOFF bit changes, suspend/resume, and remove forcing the panel dark.

# sources/distributed-fs/ceph-client/drivers/video/backlight/locomolcd.c

## Purpose
This legacy Locomo driver controls LCD power and frontlight brightness for Sharp Zaurus Collie/Poodle-era hardware.

## Important APIs, Types, and Functions
Global pointers track the Locomo device and backlight device. `locomolcd_on()` and `locomolcd_off()` sequence Locomo GPIOs, DAC/common voltage, and timing controller registers. `locomolcd_power()` is exported and wraps those sequences with local IRQ disable. `locomolcd_set_intensity()` maps brightness levels 0-4 to hard-coded `locomo_frontlight_set()` parameters and honors `LOCOMOLCD_SUSPENDED`.

## Control Flow
Module init registers a `locomo_driver` for `LOCOMO_DEVID_BACKLIGHT`. Probe stores the Locomo device, configures frontlight GPIO direction, registers `locomo-bl`, sets default brightness 2, and applies it. Suspend sets the suspended flag and reapplies intensity as zero; resume clears it and restores. Remove sets brightness zero, unregisters the backlight, and clears the global device pointer under IRQ disable.

## State and Persistence
This is single-instance global state. `current_intensity`, `locomolcd_flags`, and global device pointers are volatile. Hardware state is in Locomo GPIO/registers and DAC output.

## Dependencies and Integration Points
The driver depends on Locomo bus APIs, ARM machine detection, `sharpsl_param.comadj`, SA1100 generic headers, and the backlight core. `locomolcd_power()` is exported for other platform code.

## Risks
The file explicitly assumes old single-CPU hardware and uses local IRQ disabling rather than general locking. Long delays occur with interrupts disabled in `locomolcd_power()`. Global exported power control can race conceptually with driver remove if callers do not honor device lifetime.

## Test Signals
Test Locomo probe/remove, exported power on/off, comadj defaulting on Collie, all brightness levels including invalid values, suspend/resume, and frontlight GPIO/register sequencing.

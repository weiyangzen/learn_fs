# sources/distributed-fs/ceph-client/drivers/video/backlight/max8925_bl.c

## Purpose
This platform child driver controls Maxim MAX8925 PMIC WLED backlight registers.

## Important APIs, Types, and Functions
`struct max8925_backlight_data` stores parent chip pointer, current brightness, mode-control register, and brightness-control register. `max8925_backlight_set()` writes brightness, toggles WLED enable bit on zero/nonzero transitions, and caches brightness. `max8925_backlight_get_brightness()` reads the brightness register. `max8925_backlight_dt_init()` reads a parent `backlight` child node for `maxim,max8925-dual-string`.

## Control Flow
Probe retrieves two `IORESOURCE_REG` resources for mode/control registers, registers a raw backlight with default max brightness, optionally builds platform data from DT, programs mode bits for scaling/frequency/dual-string, and applies brightness. Runtime update writes brightness first, then enables/disables the output bit.

## State and Persistence
Brightness cache mirrors hardware after successful writes. Mode settings come from platform/DT at probe and persist in PMIC registers until changed.

## Dependencies and Integration Points
The driver depends on MAX8925 MFD helpers, platform register resources, optional OF parsing, and the backlight core. It is bound by platform name `max8925-backlight`.

## Risks
`of_get_child_by_name()` failure in DT init logs an error but silently leaves platform data unset. The DT helper allocates platform data and assigns it to `pdev->dev.platform_data`, which is an older pattern. `get_brightness()` maps any read error to `-EINVAL`, losing the original error.

## Test Signals
Test missing register resources, DT dual-string parsing, platform data mode bits, brightness clamp/enable transitions, hardware readback, MFD write failures, and probe cleanup on registration failure.

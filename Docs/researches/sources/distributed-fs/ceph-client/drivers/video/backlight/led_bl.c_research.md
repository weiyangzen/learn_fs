# sources/distributed-fs/ceph-client/drivers/video/backlight/led_bl.c

## Purpose
This platform driver aggregates one or more LED class devices into a single raw backlight device.

## Important APIs, Types, and Functions
`struct led_bl_data` stores the backlight device, LED classdev pointers, optional brightness-level table, defaults, max brightness, and enabled flag. `led_bl_set_brightness()` maps a backlight level through the optional levels table and writes every LED. `led_bl_power_off()` sets all LEDs to `LED_OFF`. `led_bl_get_leds()` resolves LED phandles and validates equal ranges. `led_bl_parse_levels()` reads `brightness-levels` and `default-brightness-level`.

## Control Flow
Probe resolves LEDs from the `leds` property, optionally maps brightness levels, registers a backlight, creates device links to LED suppliers, disables each LED's own sysfs interface while under `led_access`, and applies initial status. Remove unregisters the backlight, powers LEDs off, and reenables LED sysfs access.

## State and Persistence
The driver owns volatile aggregation state and disables direct LED sysfs control during its lifetime. Brightness values persist only in the LED class devices/hardware.

## Dependencies and Integration Points
It depends on OF LED phandles, LED class APIs, device links, and the backlight subsystem. It binds to `led-backlight`.

## Risks
`props.power` is initialized opposite of the usual expectation: default brightness greater than zero sets `BACKLIGHT_POWER_OFF`, relying on `backlight_get_brightness()` semantics. All LEDs must have identical ranges; mixed hardware cannot be used without a table or redesign. Direct LED sysfs access is disabled, which can surprise users but avoids competing control.

## Test Signals
Test no LEDs, LED lookup deferral/failure, mismatched LED ranges, brightness-level mapping, default-brightness-level validation, device-link failure rollback, LED sysfs disable/enable, and remove cleanup.

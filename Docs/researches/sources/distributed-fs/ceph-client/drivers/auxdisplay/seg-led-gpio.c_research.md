# sources/distributed-fs/ceph-client/drivers/auxdisplay/seg-led-gpio.c

## Purpose
Drives a single-character 7-segment LED display using GPIO lines. It exposes the character through the line-display core and maps the first visible character to segment GPIO values.

## Important APIs, Types, And Functions
- `struct seg_led_priv` stores the line-display instance, delayed work, and GPIO descriptor array.
- `seg_led_update()` maps `linedisp->buf[0]` to a 7-segment byte and writes all segment GPIOs.
- `seg_led_linedisp_get_map_type()` initializes work and selects `LINEDISP_MAP_SEG7`.
- `seg_led_probe()` obtains GPIO array and registers a one-character linedisp; `seg_led_remove()` cancels work and unregisters it.

## Control Flow
Probe allocates private data, stores it as platform data, gets the `"segment"` GPIO array as outputs low, validates there are 7 or 8 descriptors, and registers line-display with one character. Updates schedule immediate work so GPIO writes can sleep. Remove cancels outstanding work and unregisters the linedisp.

## State And Persistence
State is private struct plus line-display message/map state. Hardware segment state persists on GPIO outputs until the next update or device removal.

## Dependencies And Integration Points
Depends on platform/OF match `"gpio-7-segment"`, GPIO consumer arrays, bitmap helpers, 7-segment mapping, and the `LINEDISP` namespace.

## Risks And Edge Cases
Decimal point is explicitly unsupported despite allowing 8 GPIOs; the mapping writes an 8-bit value and board wiring must match map bit order. Work cancellation is required before unregistering. Invalid GPIO count fails probe.

## Test Signals
Probe with 6/7/8/9 GPIOs, sysfs message changes for known segment patterns, segment map rewrite, remove during pending update, and active-low GPIO descriptors from firmware are useful tests.

# sources/distributed-fs/ceph-client/drivers/auxdisplay/line-display.h

## Purpose
Defines the public line-display core interface for simple character and segment displays. It lets hardware drivers expose a fixed character count and update callback while the core handles sysfs messages, scrolling, and optional character-to-segment maps.

## Important APIs, Types, And Functions
- `enum linedisp_map_type` distinguishes 7-segment and 14-segment conversion maps.
- `struct linedisp_map` stores the active map type, map payload, and byte size.
- `struct linedisp_ops` provides optional `get_map_type()` and required `update()`; `update()` must not sleep.
- `struct linedisp` embeds device/timer/core state used by `line-display.c`.
- Lifecycle functions support direct attribute attachment or child device registration.

## Control Flow
Drivers embed `struct linedisp` in private state and call `linedisp_register()` or `linedisp_attach()` with character count and ops. The core initializes state and calls `ops->update()` whenever the visible buffer changes; drivers unregister/detach on teardown.

## State And Persistence
The struct exposes all core-owned per-display fields: sysfs device, scroll timer, ops, map pointer, visible buffer, full message, geometry, scroll position/rate, and ID. Drivers should treat most fields as owned by the core except for reading `buf` during update.

## Dependencies And Integration Points
Includes device/timer types and segment mapping headers. Drivers importing `LINEDISP` use this header to bind hardware-specific update functions to the generic sysfs surface.

## Risks And Edge Cases
Because `update()` cannot sleep, I2C/regmap/GPIO drivers must schedule work rather than do blocking operations directly from timer/sysfs contexts if their bus access can sleep. Mis-sized `num_chars` causes update callbacks to read wrong amounts from `buf`.

## Test Signals
Compile coverage for drivers with and without maps, map type initialization, no-sleep update assumptions, and lifecycle symmetry between register/unregister and attach/detach are the main signals.

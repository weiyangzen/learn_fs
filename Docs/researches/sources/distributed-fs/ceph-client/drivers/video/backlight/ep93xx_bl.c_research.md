# sources/distributed-fs/ceph-client/drivers/video/backlight/ep93xx_bl.c

## Purpose
This platform driver controls the EP93xx SoC LCD `BRIGHT` PWM register and exposes it as a raw 0-255 backlight.

## Important APIs, Types, and Functions
`struct ep93xxbl` stores the mapped MMIO base and cached brightness. `ep93xxbl_set()` writes `(brightness << 8) | EP93XX_MAX_COUNT` to the PWM register and updates the cache. `ep93xxbl_update_status()` and `ep93xxbl_get_brightness()` implement the backlight callbacks. PM callbacks set brightness to zero on suspend and restore by calling `backlight_update_status()` on resume.

## Control Flow
Probe allocates state, fetches the first memory resource, maps it with `devm_ioremap()`, registers a raw backlight, sets default brightness 128, and writes the register. It intentionally does not request the memory region because the framebuffer driver shares the same register block.

## State and Persistence
The cached brightness is volatile. Hardware PWM state persists in MMIO until changed; resume replays the backlight core brightness rather than the cached zero written during suspend.

## Dependencies and Integration Points
The file depends on platform resources, MMIO accessors, and the backlight core. It has an explicit integration constraint with `drivers/video/ep93xx-fb.c` because both share register space.

## Risks
Because the MMIO region is not reserved, accidental overlapping access by other drivers is possible. `devm_ioremap()` rather than `devm_ioremap_resource()` means resource conflicts and range metadata are not enforced. There is no blank-state handling beyond what `backlight_get_brightness()` provides.

## Test Signals
Check probe with missing resource, MMIO mapping failure, default register value, brightness extremes, suspend writing zero, resume restoring requested brightness, and coexistence with the EP93xx framebuffer.

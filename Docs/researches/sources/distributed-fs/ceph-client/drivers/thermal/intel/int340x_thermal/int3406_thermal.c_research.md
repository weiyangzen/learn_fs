# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3406_thermal.c

## Purpose

`int3406_thermal.c` exposes an ACPI display participant as a thermal cooling device by limiting raw backlight brightness according to firmware-provided brightness bounds.

## Important APIs, Types, and Functions

`struct int3406_thermal_data` stores ACPI brightness levels, lower/upper indexes, raw backlight device, and cooling device. Cooling callbacks map thermal cooling state to ACPI brightness levels and then to raw backlight brightness. `int3406_thermal_get_limit()` reads `DDDL` and `DDPC` to update brightness bounds. `int3406_notify()` refreshes limits on event `INT3406_BRIGHTNESS_LIMITS_CHANGED`.

## Control Flow

Probe requires an ACPI handle, a raw backlight device, and ACPI video brightness levels. It computes limits, registers a cooling device named by the ACPI BID, then installs a notify handler. Setting cooling state clamps against `upper_limit - lower_limit` and applies an indexed brightness. Reading current state converts raw brightness back to ACPI percent and selects the nearest firmware level above it.

## State and Persistence Behavior

The driver persists only runtime limit indexes and the allocated brightness table. Hardware state is the backlight brightness owned by the backlight subsystem; ACPI owns the limit policy.

## Dependencies and Integration Points

It depends on ACPI video brightness (`acpi_video_get_levels()`), raw backlight devices, ACPI notify, and thermal cooling devices. It bridges firmware DPTF display throttling with the native graphics/backlight stack.

## Risks and Test Signals

Risks include no raw backlight device at probe time, non-monotonic ACPI brightness levels, division by `max_brightness`, missing notify-handler removal in `remove()`, and ambiguous percent-to-raw mapping. Test signals include cooling state max/current/set behavior, `DDDL`/`DDPC` bound changes, backlight brightness updates, and probe failure paths that free the brightness table.

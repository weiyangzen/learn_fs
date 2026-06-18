# sources/distributed-fs/ceph-client/include/linux/rtc/rtc-omap.h

## Purpose
`rtc/rtc-omap.h` declares the OMAP RTC power-off programming hook.

## Important APIs, types, and functions
The sole API is `omap_rtc_power_off_program(struct device *dev)`, which lets OMAP platform/power code program the RTC block for power-off behavior.

## Control flow, state, and persistence
Callers pass the RTC device to `omap_rtc_power_off_program()` before system poweroff so the driver/hardware can prepare the RTC-controlled shutdown or wake path. Persistent state is hardware programming in the OMAP RTC/power domain.

## Dependencies and integration points
It depends on `struct device` from normal kernel includes and integrates OMAP RTC driver code with platform poweroff flows and the generic RTC class.

## Risks and test signals
Risks include invoking the hook on the wrong device, failing to program wake/poweroff registers before shutdown, and SoC-specific power sequencing differences. Test signals include OMAP RTC probe, system poweroff, alarm wake from poweroff/suspend, and builds where the hook is referenced by platform power code.

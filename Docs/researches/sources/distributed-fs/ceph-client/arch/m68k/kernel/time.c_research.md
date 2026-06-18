# sources/distributed-fs/ceph-client/arch/m68k/kernel/time.c

## Purpose

`time.c` supplies m68k-specific time initialization, machine RTC hook plumbing, optional generic RTC device registration, heartbeat LED behavior, and entropy hook export.

## Important APIs, Types, and Functions

It defines/export `mach_random_get_entropy`, `mach_hwclk`, `mach_get_rtc_pll`, and `mach_set_rtc_pll` where configured. Functions include `timer_heartbeat()`, `read_persistent_clock64()`, generic RTC callbacks `rtc_generic_get_time()`, `rtc_generic_set_time()`, `rtc_ioctl()`, `rtc_init()`, and `time_init()`.

## Control Flow

`time_init()` calls `mach_sched_init()`, which platform setup installed. `timer_heartbeat()` toggles `mach_heartbeat()` in a load-dependent double-pulse pattern. Classic m68k/Sun3 builds use `mach_hwclk()` to read persistent time or implement a `rtc-generic` platform device. RTC ioctl supports PLL get/set through machine hooks and requires `CAP_SYS_TIME` for setting. `rtc_init()` registers the generic RTC only if `mach_hwclk` exists.

## State and Persistence Behavior

The file owns machine hook pointers and heartbeat static counters. RTC set and PLL operations can persist into hardware NVRAM/RTC depending on platform implementation. `mach_random_get_entropy` exposes optional hardware entropy to other code.

## Dependencies and Integration Points

It depends on platform setup assigning scheduler, heartbeat, hardware clock, PLL, and entropy hooks. It integrates with generic RTC class, platform device registration, `/proc/loadavg` data via `avenrun`, and Linux timekeeping.

## Risks and Edge Cases

`time_init()` assumes `mach_sched_init` is non-null after setup; a missing platform hook will crash. RTC generic callbacks assume `mach_hwclk` remains valid. Heartbeat timing uses load average and static counters, so board LED callbacks must be cheap and IRQ-safe for timer context.

## Test Signals

Boot should initialize timer interrupts, `hwclock` or generic RTC reads should work when hooks exist, PLL ioctl should enforce permissions, and heartbeat LED pattern should track load without timer stalls.

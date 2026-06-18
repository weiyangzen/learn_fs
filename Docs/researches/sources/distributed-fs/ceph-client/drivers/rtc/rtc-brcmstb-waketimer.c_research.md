# sources/distributed-fs/ceph-client/drivers/rtc/rtc-brcmstb-waketimer.c

## Purpose
Broadcom STB wake timer RTC driver. It wraps a seconds counter and alarm comparator as an RTC, supports wakeup from suspend/poweroff, and handles separate wake and runtime alarm IRQ lines when provided.

## Important APIs, types, and functions
- `struct brcmstb_waketmr` stores RTC, MMIO base, wake/alarm IRQs, reboot notifier, optional clock/rate, cached alarm time, and alarm state booleans.
- `brcmstb_waketmr_is_pending()`, `clear_alarm()`, and `set_alarm()` manage event flags, comparator programming, prescaler setup, and IRQ enable balance.
- `brcmstb_waketmr_irq()` handles wake-only interrupts; `brcmstb_alarm_irq()` handles runtime alarm events, disables IRQs during wake-enabled expiration, and calls `rtc_update_irq()`.
- `wktmr_read()` samples seconds plus prescaler until the prescaler value is stable, producing subsecond ordering support.
- RTC ops read/write the seconds counter, cache/read alarms, program comparator, and enable/disable alarms.
- PM callbacks enable IRQ wake, catch noirq alarm races via `alarm_expired`, clear alarms on resume, and a reboot notifier arms wake behavior for `SYS_POWER_OFF`.

## Control flow
Probe maps the timer, enables optional clock or uses 27 MHz default, requests the wake IRQ, clears stale alarm state, optionally requests a second alarm IRQ with `IRQF_NO_AUTOEN`, registers reboot notifier, sets `range_max = U32_MAX`, and registers the RTC. Alarm programming always clears the previous comparator, writes prescaler and alarm time, and adjusts if the requested second is already behind the counter.

## State and persistence behavior
Hardware state is the counter, prescaler, alarm comparator, and event flag. Software caches `rtc_alarm`, `alarm_en`, and `alarm_expired` because runtime IRQ enablement and wake IRQ behavior are not fully represented by the hardware registers. Counter range is 32-bit seconds.

## Dependencies and integration points
Depends on platform MMIO resources, optional `clk`, interrupt framework, PM wakeup APIs, reboot notifier, and RTC class. It binds to OF compatible `"brcm,brcmstb-waketimer"`.

## Risks
- IRQ enable/disable balance is delicate, especially `alarm_expired` paths that re-enable a disabled IRQ to maintain nesting balance.
- `rtc_alarm` is cached in software and may not reflect externally modified hardware.
- Counter and alarm range are limited to `U32_MAX` seconds.
- Suspend/noirq race handling depends on `alarm_expired` being set only from the runtime alarm IRQ.

## Test signals
Alarm set/read/enable tests with one and two IRQ resources, suspend/resume wake tests, `SYS_POWER_OFF` notifier behavior, clock absent/zero-rate fallback, and alarms set at or before the current counter.

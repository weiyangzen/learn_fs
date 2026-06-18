# sources/distributed-fs/ceph-client/drivers/watchdog/stmp3xxx_rtc_wdt.c

## Purpose
`stmp3xxx_rtc_wdt.c` is a small watchdog frontend for STMP3xxx/i.MX23/i.MX28 RTC-based watchdog hardware. It delegates actual register programming to platform data supplied by the RTC parent.

## Important APIs, types, and functions
The driver uses module parameter `heartbeat`, static `stmp3xxx_wdd`, and platform data `struct stmp3xxx_wdt_pdata` with `wdt_set_timeout`. Watchdog ops are `wdt_start()`, `wdt_stop()`, and `wdt_set_timeout()`. Reboot behavior is handled by `wdt_notify_sys()`.

## Control flow
Probe stores the child device as watchdog drvdata, clamps heartbeat, sets parent, registers the watchdog, and registers a reboot notifier. Start calls the parent callback with timeout converted from seconds to 1 kHz ticks. Stop passes zero. Reboot notification deliberately keeps the watchdog enabled for `SYS_DOWN`, but stops it for halt and poweroff. Suspend stops if active; resume restarts if active.

## State and persistence behavior
The watchdog device is static and singleton. Hardware state is managed by the RTC parent and persists according to the parent callback. The status includes `WATCHDOG_NOWAYOUT_INIT_STATUS`, reflecting build-time nowayout policy.

## Dependencies and integration points
It depends on `<linux/stmp3xxx_rtc_wdt.h>`, platform data from an RTC MFD/parent, reboot notifiers, and watchdog core managed registration.

## Risks and test signals
Risks are null or invalid platform data, tick conversion overflow near `UINT_MAX / 1000`, static singleton limitations, and notifier behavior that intentionally leaves watchdog active during restart. Tests should validate parent callback calls, heartbeat clamping, halt/poweroff stop, restart keep-enabled behavior, and suspend/resume active-state preservation.

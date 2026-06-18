# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_hrtimer_pretimeout.c

## Purpose
This file implements software pretimeout delivery for watchdog devices that do not expose hardware pretimeout support. It uses a per-watchdog hrtimer in `watchdog_core_data` to notify the selected pretimeout governor before the full watchdog timeout expires.

## Important APIs, types, and functions
The exported framework helpers are `watchdog_hrtimer_pretimeout_init`, `watchdog_hrtimer_pretimeout_start`, and `watchdog_hrtimer_pretimeout_stop`. The timer callback `watchdog_hrtimer_pretimeout` resolves the owning `watchdog_core_data` from `pretimeout_timer` and calls `watchdog_notify_pretimeout`.

## Control flow
Device registration initializes the hrtimer. Each successful hardware start or ping calls `watchdog_hrtimer_pretimeout_start`. If the device lacks hardware `WDIOF_PRETIMEOUT` but has a valid nonzero `wdd->pretimeout`, the timer is armed for `timeout - pretimeout` seconds. Otherwise it is cancelled. When the timer fires it invokes the governor and does not restart itself; the next watchdog ping/start rearms it.

## State and persistence
State is limited to the hrtimer embedded in watchdog core data and the current `wdd->timeout`/`wdd->pretimeout` values. Nothing persists across unregister or reboot.

## Dependencies and integration points
It depends on Linux hrtimers, `struct watchdog_device`, `watchdog_core.h`, and the pretimeout governor interface in `watchdog_pretimeout.h`. It is called only by the generic watchdog device layer.

## Risks and test signals
Risks are off-by-one timer scheduling, stale timer callbacks after unregister, double-notification when hardware already provides pretimeout, and invalid pretimeout values. Test signals include devices with software-only pretimeout, hardware pretimeout devices, timeout changes that invalidate pretimeout, repeated ping rearming, stop/unregister cancellation, and governor callback invocation timing.

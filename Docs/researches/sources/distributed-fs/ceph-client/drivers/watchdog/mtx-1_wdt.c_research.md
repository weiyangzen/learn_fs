# sources/distributed-fs/ceph-client/drivers/watchdog/mtx-1_wdt.c

## Purpose
`mtx-1_wdt.c` is a legacy miscdevice watchdog for the MTX-1 board. It toggles a GPIO periodically and exposes `/dev/watchdog` ioctls for keepalive and enable/disable.

## Important APIs, types, and functions
The global `mtx1_wdt_device` stores a GPIO descriptor, timer, completion, spinlock, queue/running counters, timeout ticks, and single-open bit. Important routines are `mtx1_wdt_trigger`, `mtx1_wdt_start`, `mtx1_wdt_stop`, `mtx1_wdt_reset`, `mtx1_wdt_open`, `mtx1_wdt_write`, and `mtx1_wdt_ioctl`.

## Control flow
Probe acquires the watchdog GPIO as output high, initializes state, registers `/dev/watchdog`, and starts the background timer. The timer toggles the GPIO every five seconds while queued, decrements `ticks` if running, and either requeues itself or completes removal. Writes and `WDIOC_KEEPALIVE` reset `ticks`; `WDIOC_SETOPTIONS` starts or stops the timer. Remove disables queueing, waits for completion if needed, and deregisters the miscdevice.

## State and persistence
State is entirely global runtime state. The GPIO level and periodic timer represent the hardware feed signal. There is no bootstatus, no magic-close, and no persistent configuration beyond module lifetime.

## Dependencies and integration points
It depends on platform device alias `mtx1-wdt`, GPIO descriptor APIs, timer/completion primitives, miscdevice `WATCHDOG_MINOR`, and classic watchdog ioctls rather than the watchdog core.

## Risks and test signals
Risks include global singleton behavior, the remove path's noted unlocked queue check, lack of nowayout/magic-close semantics, `ticks` in jiffies but decremented once per timer interval, and timer/GPIO races on removal. Test signals include single-open enforcement, keepalive timeout expiry, enable/disable ioctl behavior, removal while timer queued, GPIO request failure, and userspace write with zero length.

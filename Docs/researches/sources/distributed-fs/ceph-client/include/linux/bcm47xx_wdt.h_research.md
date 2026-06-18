# sources/distributed-fs/ceph-client/include/linux/bcm47xx_wdt.h

## Purpose
Defines the BCM47xx watchdog device wrapper tying hardware timer operations, a generic `watchdog_device`, and optional software timer fallback state together.

## Important APIs, types, and functions
- `struct bcm47xx_wdt` stores hardware timer callbacks `timer_set()` and `timer_set_ms()`, `max_timer_ms`, driver-private data, embedded `watchdog_device`, `soft_timer`, and `soft_ticks`.
- `bcm47xx_wdt_get_drvdata()` returns driver-private data.

## Control flow and state
The watchdog driver fills the structure with timer callbacks and registers the embedded watchdog device. Runtime pings program the hardware timer directly or maintain a software timer that refreshes hardware before its maximum interval expires.

## State and persistence behavior
State is runtime watchdog state. Hardware timer state can outlive Linux if not stopped, but this header only describes in-memory bookkeeping and callbacks.

## Dependencies and integration points
Depends on kernel timers, atomics via included types, and watchdog framework. Integrated by BCM47xx chipcommon/watchdog drivers.

## Risks
Callback units must be respected (`timer_set` ticks versus `timer_set_ms` milliseconds). `soft_ticks` is atomic because soft timer and watchdog operations can race. Incorrect `max_timer_ms` can allow premature resets or ineffective pings.

## Test signals
Exercise watchdog start/stop/ping, timeout values above and below hardware maximum, software timer refresh, driver-data retrieval, and shutdown/reboot behavior.

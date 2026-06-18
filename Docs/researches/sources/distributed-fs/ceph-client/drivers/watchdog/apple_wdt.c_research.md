# sources/distributed-fs/ceph-client/drivers/watchdog/apple_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/apple_wdt.c` is a watchdog-core platform driver for Apple SoC watchdog hardware. It uses watchdog channel WD1 for normal machine reset, provides restart support, and restores active watchdog state across suspend/resume. The complete 238-line source was read for this report.

## Important APIs, Types, and Functions

`struct apple_wdt` stores an embedded `watchdog_device`, MMIO base, and clock rate. Operations are `apple_wdt_start()`, `apple_wdt_stop()`, `apple_wdt_ping()`, `apple_wdt_set_timeout()`, `apple_wdt_get_timeleft()`, and `apple_wdt_restart()`. Probe is `apple_wdt_probe()`, with PM hooks `apple_wdt_suspend()` and `apple_wdt_resume()`. The OF match is `apple,wdt`.

## Control Flow

Probe allocates state, maps registers, enables and reads the clock, computes maximum hardware heartbeat from a 32-bit counter, detects whether WD1 reset is already enabled and marks `WDOG_HW_RUNNING`, initializes timeout, writes the bite time, arranges stop-on-unregister, sets restart priority, and registers the device. Start clears WD1 current time and enables reset. Ping resets current time. Timeout writes WD1 bite time, clamping the hardware interval to `max_hw_heartbeat_ms` while preserving userspace timeout in `wdd->timeout`. Restart enables WD1 reset, sets bite and current time to zero, flushes writes, and waits about 150 ms.

## State and Persistence Behavior

Runtime state is in `watchdog_device` and WD1 MMIO registers. Existing bootloader-enabled WD1 state is detected. Suspend stops if active or hardware-running; resume restarts under the same condition. No nonvolatile state is stored.

## Dependencies and Integration Points

The driver depends on OF platform binding `apple,wdt`, clock framework, MMIO access, watchdog core, and restart priority integration. It is selected by `APPLE_WATCHDOG` and built as `apple_wdt.o`.

## Risks and Edge Cases

Only WD1 is used; WD0 interrupt/pretimeout capability is documented but not implemented. `get_timeleft()` subtracts current from reset time and assumes no wrap or current greater than reset. Large requested timeouts rely on watchdog core max-hw-heartbeat management. Restart timing is based on observed reset latency.

## Test Signals

Test clock-rate zero failure, boot-running detection, timeout clamping, ping/start/stop register writes, restart reset timing, suspend/resume for active and inactive devices, and watchdog core handling of timeouts longer than hardware max.

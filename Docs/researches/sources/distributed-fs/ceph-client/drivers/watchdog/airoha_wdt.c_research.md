# sources/distributed-fs/ceph-client/drivers/watchdog/airoha_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/airoha_wdt.c` is a watchdog-core platform driver for the Airoha EN7581 SoC watchdog timer, implemented using timer3 registers. It maps MMIO registers, derives the watchdog tick rate from the bus clock, and exposes start/stop/ping/timeout/timeleft operations. The complete 216-line source was read for this report.

## Important APIs, Types, and Functions

`struct airoha_wdt_desc` stores the embedded `watchdog_device`, computed `wdt_freq`, and MMIO base. Module parameters are `heartbeat` and `nowayout`. Operations are `airoha_wdt_start()`, `airoha_wdt_stop()`, `airoha_wdt_ping()`, `airoha_wdt_set_timeout()`, and `airoha_wdt_get_timeleft()`. Probe is `airoha_wdt_probe()`, and PM hooks are `airoha_wdt_suspend()` and `airoha_wdt_resume()`.

## Control Flow

Probe allocates state, maps resource 0, enables the `bus` clock, computes watchdog frequency as half the bus clock, initializes the watchdog device, sets max timeout from the 32-bit timer field, applies nowayout and stop-on-unregister, then registers the device. Start enables the watchdog timer, watchdog reset, and timer interrupt bits, then writes load value as timeout times watchdog frequency. Ping writes the reload bit. Setting timeout restarts the hardware when active. Suspend stops active watchdogs; resume restarts and pings active watchdogs.

## State and Persistence Behavior

Runtime state is in watchdog-core fields and MMIO timer registers. The driver does not persist configuration beyond the active device. During suspend it stops hardware if active, then restores on resume based on watchdog-core active state.

## Dependencies and Integration Points

It depends on platform device resources, OF compatible `airoha,en7581-wdt`, clock framework, MMIO accessors, bitfield helpers, and watchdog core. Kconfig `AIROHA_WATCHDOG` selects `WATCHDOG_CORE`; Makefile maps it to `airoha_wdt.o`.

## Risks and Edge Cases

The stop path uses `val &= (~WDT_ENABLE & ~WDT_TIMER_ENABLE)`, which relies on bitwise combination behavior and deserves review if flags change. `wdt_freq` depends on a nonzero clock rate, but the code does not explicitly reject zero. Restarting on timeout change leaves a short stop/start window. Suspend stops the watchdog even under nowayout policy if watchdog core calls suspend.

## Test Signals

Test DT matching, bus clock enable failure, max-timeout calculation, start register bits, reload writes, get-timeleft conversion, timeout change while inactive and active, and suspend/resume restoration.

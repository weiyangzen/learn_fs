# sources/distributed-fs/ceph-client/drivers/watchdog/ath79_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/ath79_wdt.c` is a legacy miscdevice watchdog driver for Atheros AR71xx/AR724x/AR913x SoC watchdog hardware. It maps watchdog registers, derives maximum timeout from the watchdog clock, and exposes `/dev/watchdog` ioctls. The complete 322-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `nowayout` and `timeout`. Global state includes `wdt_flags`, `wdt_clk`, `wdt_freq`, `boot_status`, `max_timeout`, and `wdt_base`. Hardware helpers are `ath79_wdt_wr()`, `ath79_wdt_rr()`, `ath79_wdt_keepalive()`, `ath79_wdt_enable()`, `ath79_wdt_disable()`, and `ath79_wdt_set_timeout()`. File operations are `ath79_wdt_open()`, `ath79_wdt_release()`, `ath79_wdt_write()`, and `ath79_wdt_ioctl()`. Platform lifecycle functions are `ath79_wdt_probe()`, `ath79_wdt_remove()`, and `ath79_wdt_shutdown()`.

## Control Flow

Probe maps registers, enables the `wdt` clock, computes timeout limits, clamps invalid module timeout to max, records boot status from the last-reset bit, and registers `/dev/watchdog`. Open sets busy state, clears magic-close expectation, and enables the hardware. Writes scan for `V` when nowayout is false and reload the timer. Ioctls return support/status/bootstatus, keepalive, and set/get timeout. Release disables only if magic close is set; otherwise it logs and refreshes. Shutdown disables the hardware.

## State and Persistence Behavior

Software state is global and singleton. Hardware state lives in the timer and control registers. Boot reset cause is latched in `boot_status` at probe from `WDOG_CTRL_LAST_RESET`.

## Dependencies and Integration Points

It depends on platform resources, OF compatible `qca,ar7130-wdt`, clock framework, MMIO, miscdevice, and watchdog ioctl ABI. Kconfig `ATH79_WDT` maps to `ath79_wdt.o`.

## Risks and Edge Cases

The driver is legacy and not watchdog-core based. Global state prevents multiple instances. Register writes are flushed by reads because hardware update ordering matters; removing flushes could break enable/disable. Enabling delays two microseconds to let the timer register update on AR934x.

## Test Signals

Test clock-rate zero, max-timeout calculation, bootstatus reporting, magic close, nowayout, timeout boundary handling, readback flush behavior, and shutdown disable.

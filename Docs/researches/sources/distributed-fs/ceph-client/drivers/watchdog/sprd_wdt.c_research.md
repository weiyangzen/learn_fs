# sources/distributed-fs/ceph-client/drivers/watchdog/sprd_wdt.c

## Purpose
`sprd_wdt.c` drives Spreadtrum watchdog controllers with separate enable and RTC clocks, lock/unlock-protected registers, reset and interrupt/pretimeout support, and suspend/resume integration.

## Important APIs, types, and functions
`struct sprd_wdt` holds MMIO base, watchdog device, two clocks, and IRQ. Helpers include `sprd_wdt_lock()`, `sprd_wdt_unlock()`, `sprd_wdt_get_cnt_value()`, `sprd_wdt_load_value()`, `sprd_wdt_enable()`, and managed cleanup `sprd_wdt_disable()`. Watchdog ops are `sprd_wdt_start()`, `sprd_wdt_stop()`, `sprd_wdt_set_timeout()`, `sprd_wdt_set_pretimeout()`, and `sprd_wdt_get_timeleft()`. `sprd_wdt_isr()` clears interrupt and notifies pretimeout.

## Control flow
Probe maps registers, gets clocks, requests the IRQ with `IRQF_NO_SUSPEND`, initializes 3..60 second limits, enables both clocks and the new-version bit, registers cleanup, sets nowayout from Kconfig, initializes timeout, and registers. Starting waits for the load-busy bit to clear, writes timeout and pretimeout counters split into high/low registers, enables count/interrupt/reset bits, and sets `WDOG_HW_RUNNING`. Stop clears those enable bits. Suspend stops an active watchdog and fully disables clocks; resume re-enables clocks and restarts if active.

## State and persistence behavior
The watchdog timeout/pretimeout values are in core fields and load registers. The controller has explicit lock state and busy state; clock state is owned by enable/disable helpers. No durable software state exists.

## Dependencies and integration points
It integrates with platform resources, device tree compatible `sprd,sp9860-wdt`, two named clocks, IRQ pretimeout notification, PM sleep ops, and watchdog core.

## Risks and test signals
Risks include busy-bit timeout causing failed pings, pretimeout validation allowing values greater than timeout if core does not reject them, clock imbalance on error paths, and interrupt clear races. Tests should cover clock failure unwind, IRQ pretimeout delivery, busy polling timeout, start/stop bit updates, timeout/pretimeout reloads, time-left conversion, and suspend/resume restart behavior.

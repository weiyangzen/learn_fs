<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rt2880_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rt2880_wdt.c

Purpose: watchdog-core driver for Ralink/MediaTek RT288x/RT3xxx/MT76xx timer1 watchdog hardware.

Important APIs, types, and functions: `struct rt2880_wdt_data` stores MMIO base, divided clock frequency, clock/reset handles, and watchdog. Key routines are `rt288x_wdt_ping()`, `rt288x_wdt_start()`, `rt288x_wdt_stop()`, `rt288x_wdt_set_timeout()`, `rt288x_wdt_bootcause()`, and probe.

Control flow: probe maps timer registers, gets clock, optionally deasserts reset, computes the prescaled frequency, fills watchdog limits, reads boot cause from the SoC reset-status register, initializes timeout, sets nowayout, and registers. Start configures timer1 as watchdog mode with 65536 prescale, loads timeout counts, and enables. Stop reloads and clears enable. Set-timeout updates software timeout and reloads hardware.

State and persistence behavior: state is hardware timer control/load registers, SoC reset-status bit, selected timeout, clock-derived frequency, and optional reset controller state.

Dependencies and integration points: depends on Ralink architecture `rt_sysc_r32()`, clocks, reset controller, platform MMIO, OF compatible, and watchdog core stop-on-reboot.

Risks and edge cases: `wdt->max_timeout = 0xffff / freq` can become zero if the prescaled clock is too high. Probe returns 0 even if `devm_watchdog_register_device()` fails, losing error propagation. Optional reset deassert errors are ignored when the reset is absent but also ignored if deassert fails.

Test signals: clock-rate extremes, reset status bootcause, start/stop register programming, timeout reload, failed registration behavior, and reset-controller failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rt2880_wdt.c -->

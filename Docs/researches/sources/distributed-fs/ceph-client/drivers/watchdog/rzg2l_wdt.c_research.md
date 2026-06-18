<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzg2l_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rzg2l_wdt.c

Purpose: watchdog-core driver for Renesas RZ/G2L and RZ/V2M watchdogs, using reset controls, runtime PM, and two different restart mechanisms.

Important APIs, types, and functions: `struct rzg2l_wdt_priv` stores MMIO base, watchdog, reset controller, oscillator/PCLK rates, register delay, clocks, and device type. Important functions are `rzg2l_wdt_write()`, `rzg2l_wdt_init_timeout()`, start/stop/set-timeout/restart/ping, PM disable action, probe, and suspend/resume callbacks.

Control flow: probe maps registers, gets `oscclk` and `pclk`, computes synchronization delay, gets reset control, enables IRQ-safe runtime PM, sets watchdog bounds, nowayout, stop-on-unregister, timeout, and registers. Start resumes PM, deasserts reset, clears interrupt/lapsed time, programs timeout for two overflow cycles, clears counter, and enables. Stop asserts reset and runtime-suspends. Timeout changes stop/start active hardware. Restart powers hardware, then either forces parity error on RZ/G2L or resets/programs zero timeout on RZ/V2M.

State and persistence behavior: state is reset assertion, PM usage, programmed WDTSET/WDTTIM/WDTCNT/WDTINT registers, selected timeout, and device-type-specific restart path.

Dependencies and integration points: depends on clocks, reset controller, PM runtime/genpd IRQ-safe behavior, OF match data, Linux units helpers, and watchdog core restart.

Risks and edge cases: register writes require calculated synchronization delays. Restart intentionally leaves PM usage elevated for reboot. Active timeout changes reset the block, creating a short watchdog blind spot. `WDTSET` is only 12 bits.

Test signals: RZ/G2L versus RZ/V2M restart, PM/reset error injection, active timeout update, suspend/resume active and inactive states, max timeout calculation, and register delay correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzg2l_wdt.c -->

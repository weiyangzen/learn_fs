# sources/distributed-fs/ceph-client/drivers/watchdog/starfive-wdt.c

## Purpose
`starfive-wdt.c` drives StarFive JH7100 and JH7110 watchdogs. It abstracts variant register layouts, handles locked registers, runtime PM, resets, two-clock enablement, optional early start, get-timeleft, and two-stage timeout behavior on JH7110.

## Important APIs, types, and functions
`struct starfive_wdt_variant` describes register offsets, unlock key, bit shifts, interrupt-clear polling, and `double_timeout`. `struct starfive_wdt` stores watchdog, spinlock, MMIO, clocks, variant, frequency, count, and suspend reload value. Important functions include clock/reset helpers, `starfive_wdt_unlock()/lock()`, `starfive_wdt_int_clr()`, `starfive_wdt_set_reload_count()`, `starfive_wdt_max_timeout()`, `starfive_wdt_get_timeleft()`, `starfive_wdt_keepalive()`, `starfive_wdt_start()`, `starfive_wdt_stop()`, PM wrappers, timeout setter, probe/remove/shutdown, and runtime/system PM callbacks.

## Control flow
Probe maps MMIO, gets clocks, enables runtime PM or clocks, deasserts resets, selects variant from DT, computes max timeout, initializes timeout, programs count, applies nowayout and reboot/unregister stop policy, then either starts early and marks hardware running or stops the block before registration. Start unlocks, disables for safety, enables reset, clears pending interrupt, loads count, enables, and relocks. Timeout changes recompute count, halving it for double-timeout variants, then reload while enabled.

## State and persistence behavior
Per-device state tracks the encoded count and saved suspend reload count. Hardware lock state is bracketed by the spinlock. Runtime PM owns clock enable state; system suspend saves current count, stops the watchdog, force-suspends, and resume restores the saved count and restarts active devices.

## Dependencies and integration points
It depends on DT compatibles `starfive,jh7100-wdt` and `starfive,jh7110-wdt`, clock names `apb` and `core`, reset arrays, PM runtime, watchdog core, and register polling.

## Risks and test signals
Risks include overflow in `timeout * freq`, double-timeout off-by-one behavior, failure to release runtime PM after early probe errors, and lock/unlock imbalance. Tests should cover both variants, interrupt-clear polling timeout, max-timeout math, early_enable, runtime PM start/stop, suspend/resume active and inactive cases, get-timeleft before/after IRQ status, and restart/shutdown policy.

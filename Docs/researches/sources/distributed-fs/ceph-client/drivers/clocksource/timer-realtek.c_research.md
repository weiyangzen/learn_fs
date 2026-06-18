# sources/distributed-fs/ceph-client/drivers/clocksource/timer-realtek.c

Purpose: Realtek RTD1625 system timer clockevent driver using a 64-bit timestamp comparator. It does not register a clocksource.

Important APIs/types/functions: global `systimer_base`; `rtk_ts64_read()` reads low then high timestamp words; `rtk_cmp_value_write()` writes high/low compare value; `rtk_cmp_en_write()` toggles comparator with write-enable bit. `rtk_syst_clkevt_next_event()` programs current timestamp plus cycles. `rtk_ts_match_intr_handler()` disables comparator, clears status, and dispatches.

Control flow: init acquires base/IRQ through `timer_of_init()` and registers a dynamic one-shot clockevent at fixed 1 MHz with min delta 0x64. Shutdown disables comparator, clears compare value and pending status. One-shot state also routes to shutdown, so actual arming occurs only in `set_next_event()`.

State/persistence: static `rtk_timer_to` and global base persist. Comparator enable/value registers define runtime state.

Dependencies/integration: compatible `realtek,rtd1625-systimer`, `timer-of`, IRQ polling/timer flags, fixed timer rate.

Risks: no source registration means another clocksource must exist; low/high timestamp read lacks retry if high changes after low; fixed 1 MHz rate must match hardware; clear-status writes combine read status and clear bit. Test signals include one-shot comparator interrupts, min-delta behavior, correct status clearing, and coexistence with platform clocksource.

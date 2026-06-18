# sources/distributed-fs/ceph-client/drivers/clocksource/timer-pxa.c

Purpose: Marvell/Intel PXA OS timer driver providing OSCR clocksource/sched_clock and OSMR0 one-shot clockevent for DT and legacy non-DT boards.

Important APIs/types/functions: global `timer_base`; `pxa_ost0_interrupt()` disarms OIER_E0, clears OSSR_M0, and dispatches. `pxa_osmr0_set_next_event()` writes match as OSCR plus delta and checks `MIN_OSCR_DELTA`. `pxa_timer_common_init()` registers shared clocksource/clockevent; `pxa_timer_nodt_init()` supports legacy boards.

Control flow: DT init maps shared timer/watchdog registers, gets/enables clock, parses IRQ0, then calls common init. Common init disables all timer IRQs, clears match status, registers sched_clock, requests IRQ, registers MMIO clocksource, and configures one-shot clockevent. PM suspend stores OSMR/OIER/OSCR and resume restores while ensuring OSMR0 is safely ahead.

State/persistence: global base plus optional PM save arrays persist. Clockevent is a static object. Registers are shared with watchdog channel/enable register.

Dependencies/integration: compatible `marvell,pxa-timer`, legacy `clk_get(NULL, "OSTIMER0")`, `<clocksource/pxa.h>`, PM hooks, sched_clock.

Risks: no periodic mode; shared watchdog registers; clocksource init failure after IRQ request does not free IRQ; resume writes OSCR which can affect monotonicity but adjusts match instead where needed. Test signals include min-delta `-ETIME` avoidance, suspend/resume wake tick, DT and non-DT init, and OSCR clocksource stability.

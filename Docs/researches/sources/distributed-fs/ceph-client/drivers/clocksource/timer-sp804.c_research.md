# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sp804.c

Purpose: ARM/HiSilicon SP804 dual-timer driver supporting clocksource/sched_clock/delay timer and clockevent roles, plus Integrator/CP two-node handling.

Important APIs/types/functions: variant descriptors `arm_sp804_timer` and `hisi_sp804_timer`; `sp804_clkevt` array resolves timer channel MMIO; `sp804_clocksource_and_sched_clock_init()` initializes a down-counting source; `sp804_clockevents_init()` initializes common event timer and IRQ; `sp804_of_init()` chooses timer1/timer2 roles based on `arm,sp804-has-irq`.

Control flow: common OF init skips after first device, maps base, disables both timers, obtains clocks, parses IRQ, initializes channel pointer table, then selects event/source channel. Source path loads all-ones, enables periodic mode, registers MMIO clocksource, optional delay timer, and sched_clock. Event path computes reload, requests IRQ, and registers clockevent. Integrator/CP path uses call count: first node source, second event.

State/persistence: static channel array, `common_clkevt`, `sched_clkevt`, delay pointers, and initialized/init_count gates. Event handling is global, so one event timer at a time.

Dependencies/integration: compatibles `arm,sp804`, `hisilicon,sp804`, `arm,integrator-cp-timer`, `timer-sp.h`, optional ARM delay, CCF clocks.

Risks: request_irq failure only logs but still registers clockevent; HiSilicon 64-bit descriptor still registers 32-bit source read; single-device gate ignores additional SP804s; clock selection with three parent clocks is subtle. Tests should cover role property, Integrator call count, clock rates, IRQ clear, and delay/sched_clock registration.

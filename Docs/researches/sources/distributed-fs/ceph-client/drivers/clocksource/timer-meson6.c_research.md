# sources/distributed-fs/ceph-client/drivers/clocksource/timer-meson6.c

Purpose: Amlogic Meson6 timer driver using Timer E as 1 MHz clocksource/sched_clock/delay timer and Timer A as periodic/one-shot clockevent.

Important APIs/types/functions: global `timer_base`; `meson6_clkevt_time_stop/setup/start()` control Timer A; `meson6_timer_sched_read()` reads Timer E; `meson6_clockevent` describes clockevent callbacks; `meson6_timer_init()` wires DT resources and framework registration.

Control flow: init maps registers, parses IRQ, configures Timer E input clock to 1 us, registers sched_clock and MMIO clocksource, configures Timer A input clock to 1 us, stops Timer A, requests IRQ, fills cpumask/IRQ, and registers clockevent. Periodic mode loads `USEC_PER_SEC / HZ - 1`; one-shot mode starts nonperiodic and next-event reloads Timer A.

State/persistence: one global MMIO base for both timers. Timer E remains enabled as source; Timer A mode is controlled by event callbacks.

Dependencies/integration: compatible `amlogic,meson6-timer`, DT IRQ/base, clocksource/clockevents/sched_clock, optional ARM delay timer.

Risks: fixed 1 MHz programming assumes mux definitions and hardware behavior; init error paths do not consistently unmap; ISR does not explicitly acknowledge beyond hardware mode behavior; global singleton. Test signals include Timer E monotonicity, one-shot/periodic tick, ARM delay calibration, and correct mux register programming.

# sources/distributed-fs/ceph-client/drivers/clocksource/timer-rda.c

Purpose: RDA8810PL timer driver using OSTIMER as clockevent and 64-bit HWTIMER as clocksource/sched_clock.

Important APIs/types/functions: static `rda_ostimer_of` uses `timer-of` with named base `rda-timer` and named IRQ `ostimer`. `rda_ostimer_start/stop()` program load low/control high bits and IRQ mask. `rda_hwtimer_clocksource_read()` reads low then high with a high-stability loop. `rda_hwtimer_clocksource` is a 64-bit continuous source.

Control flow: init calls `timer_of_init()`, registers the HWTIMER clocksource at fixed 2 MHz, registers sched_clock, then registers OSTIMER clockevent. Periodic mode computes cycles per jiffy from clockevent mult/shift, starts repeat mode; next-event starts one-shot; ISR clears OSTIMER IRQ and dispatches if handler exists.

State/persistence: one static `timer_of`; clocksource read reuses the same base as OSTIMER. Hardware IRQ mask and control registers carry event mode.

Dependencies/integration: compatible `rda,8810pl-timer`, named DT resource/IRQ, fixed rate assumption, clocksource/clockevents/sched_clock.

Risks: rate is hard-coded rather than from DT clock; HWTIMER and OSTIMER share one mapped base; no clock resource; event min/max uses `UINT_MAX` though OSTIMER load has 56 bits. Tests include fixed-rate validation, 64-bit read ordering, named IRQ lookup, periodic and one-shot events, and suspend wake behavior if used.

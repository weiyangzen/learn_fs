# sources/distributed-fs/ceph-client/drivers/clocksource/timer-milbeaut.c

Purpose: Socionext Milbeaut timer driver using channel 1 as down-counting clocksource/sched_clock and channel 0 as clockevent.

Important APIs/types/functions: static `timer_of to`; `mlb_config_clock_source()` configures source channel reload and count; `mlb_evt_timer_*()` helpers program event channel; `mlb_timer_interrupt()` clears underflow and dispatches. Clockevent callbacks implement periodic, one-shot, shutdown, and next-event.

Control flow: init acquires base/clock/IRQ via `timer_of_init()`, halves the source rate due to `MLB_TMR_DIV_CNT`, starts source channel in reload/count mode, registers down-counting clocksource and sched_clock, initializes event channel, then registers clockevent. Periodic writes `of_clk.period`, one-shot/next-event stop and restart without reload bit.

State/persistence: global `to` stores all resources. Timer channel registers persist clocksource and event state. Sched_clock reads inverted source timer value.

Dependencies/integration: compatible `socionext,milbeaut-timer`, `timer-of`, clocksource/clockevents/sched_clock, DT clock/IRQ.

Risks: clockevent registration uses `timer_of_rate()` rather than the divided source rate, so event and source rates intentionally differ; W1C/underflow clearing depends on writing modified TMCSR; singleton only. Test signals include underflow IRQ clearing, source rate correctness, periodic and one-shot behavior, and clocksource monotonicity for the down counter.

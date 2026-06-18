# sources/distributed-fs/ceph-client/drivers/clocksource/timer-orion.c

Purpose: Marvell Orion timer driver using timer0 as free-running down-counting clocksource/sched_clock/delay and timer1 as clockevent.

Important APIs/types/functions: global `timer_base` and `ticks_per_jiffy`; `orion_clkevt_next_event()`, shutdown, and periodic callbacks manipulate timer1 registers with `atomic_io_modify()`. `orion_timer_init()` performs DT resource setup and framework registration.

Control flow: init maps shared timer/watchdog registers, enables clock, parses timer1 IRQ at index 1, starts timer0 with reload/value `~0`, registers down-counting clocksource and sched_clock, requests timer1 IRQ, computes ticks-per-jiffy, registers clockevent, and registers delay timer. The clockevent ISR directly calls `orion_clkevt.event_handler()`; hardware status clearing is presumably handled by timer mode/control.

State/persistence: global base and clockevent object are boot lifetime. Timer registers are shared with watchdog hardware. Delay timer and sched_clock point at timer0.

Dependencies/integration: compatible `marvell,orion-timer`, clock, IRQ index 1, `atomic_io_modify()`, clocksource/clockevents/delay.

Risks: shared watchdog register block, no explicit interrupt status ack in ISR, cleanup gaps on resource failure, and CPU0-only cpumask. Test signals include IRQ index correctness, timer0 monotonic down-read, one-shot/periodic timer1 delivery, delay timer operation, and watchdog coexistence.

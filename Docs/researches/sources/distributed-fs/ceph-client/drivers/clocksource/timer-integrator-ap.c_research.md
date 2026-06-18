# sources/distributed-fs/ceph-client/drivers/clocksource/timer-integrator-ap.c

Purpose: ARM Integrator/AP timer driver using one SP-style timer as 16-bit clocksource/sched_clock and another as periodic/one-shot clockevent, chosen by DT aliases.

Important APIs/types/functions: uses `timer-sp.h` register definitions. `integrator_clocksource_init()` configures a down-counting periodic source with optional div16. `integrator_clockevent_init()` computes divisor/reload, requests IRQ, and registers `integrator_clockevent`. Clockevent callbacks manipulate `TIMER_LOAD` and `TIMER_CTRL`.

Control flow: OF init maps the timer node, enables its clock, disables the timer, then reads `arm,timer-primary` or `arm,timer-secondary` from `/aliases`. Primary initializes clocksource; secondary parses IRQ and initializes clockevent; other nodes are disabled/ignored. The ISR clears `TIMER_INTCLR` and dispatches the event handler.

State/persistence: `sched_clk_base`, `clkevt_base`, and `timer_reload` are global. Timer role is persisted only by hardware registers and alias selection; no dynamic removal path.

Dependencies/integration: DT compatible `arm,integrator-timer`, `/aliases` properties, one clock per node, IRQ on secondary, clocksource/clockevents/sched_clock.

Risks: alias path handling is critical; comments note primary lacks IRQ. Error paths do not consistently unmap/disable clocks. 16-bit counter has limited range and uses divisors to fit rates. Tests should boot with primary/secondary aliases, check exactly one clocksource and one clockevent, verify periodic tick and one-shot mode, and inspect warnings for unused timers.

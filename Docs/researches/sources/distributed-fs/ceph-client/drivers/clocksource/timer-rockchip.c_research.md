# sources/distributed-fs/ceph-client/drivers/clocksource/timer-rockchip.c

Purpose: Rockchip RK3288/RK3399 timer driver assigning first matching timer node to clockevent and second to clocksource/sched_clock.

Important APIs/types/functions: `struct rk_timer` stores base/control pointer/clocks/frequency/IRQ; `struct rk_clkevt` embeds clockevent plus timer. `rk_timer_probe()` maps and enables clocks, selects control register offset by compatible, and parses IRQ. `rk_clkevt_init()` and `rk_clksrc_init()` build framework devices.

Control flow: `rk_timer_init()` checks global pointers: first call initializes event, second initializes source, further calls fail. Clockevent next/periodic disable, load counter low/high, then enable with user/free-running and interrupt flags. ISR clears status, disables oneshot, and dispatches. Clocksource init loads UINT_MAX, enables timer, registers down-counting MMIO source, and sched_clock.

State/persistence: global `rk_clkevt` and `rk_clksrc` pointers persist, with `ERR_PTR` used to prevent repeated init after failure. Source and event require separate hardware timer nodes.

Dependencies/integration: compatibles `rockchip,rk3288-timer` and `rockchip,rk3399-timer`, named `pclk` and `timer` clocks, DT IRQ, clocksource/clockevents.

Risks: DT node order determines role; first timer must be suitable for IRQ clockevent and second for source; cleanup does not release IRQ mapping; control register offset mismatch breaks RK3399. Test signals include two-node boot order, pclk/timer clock enable, down-count source, oneshot disable after ISR, and too-many-timers log.

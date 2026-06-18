# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/hwt.c

Purpose: Implements the FBI board hardware timer driver for the 82C54-style timer block used by SMT timers and interrupt forcing.

Important APIs/types/functions: Provides `hwt_start()`, `hwt_stop()`, `hwt_init()`, `hwt_restart()`, `hwt_read()`, and PCI-only `hwt_quick_read()`/`hwt_wait_time()`. `HWT_MAX` caps requested 16 microsecond ticks at 65000.

Control flow: `hwt_start()` clamps the requested 16 us interval, stores `t_start`, programs `B2_TI_INI` with `count * 200`, starts the timer, and marks it active. `hwt_stop()` stops the timer, clears the timer IRQ, and marks it inactive. `hwt_read()` stops an active timer, reads the remaining value, checks ISR timer expiry/wrap, stores elapsed time in `t_stop`, and returns it. The PCI quick-read path briefly stops/reloads/restarts the current timer value and can busy-wait until a duration has elapsed.

State and persistence behavior: Uses `smc->hw.t_start`, `smc->hw.t_stop`, and `smc->hw.timer_activ`. Hardware timer registers hold the active countdown until stopped or expired. Values are runtime-only and reset during hardware initialization.

Dependencies and integration points: Uses `ADDR()`, timer register constants such as `B2_TI_INI`, `B2_TI_CRTL`, `B2_TI_VAL`, `TIM_START`, `TIM_STOP`, `TIM_CL_IRQ`, and `GET_ISR()/IS_TIMINT`. Timer expiry is consumed by `timer_irq()` and then converted into SMT events by the timer package.

Risks: Unit conversion is easy to misread: API time is 16 us ticks, while programmed hardware values are multiplied by 200. `hwt_read()` stops the timer, so callers expecting a non-destructive read must use PCI `hwt_quick_read()`. Busy-wait logic returns immediately if the timer appears stopped, and wrap handling depends on monotonic countdown behavior.

Test signals: Start with zero, small, and above-maximum intervals; verify interrupt clear on stop; read before expiry and after expiry; PCI quick-read should preserve the programmed interval; `hwt_wait_time()` should handle non-wrapped and wrapped countdown cases.

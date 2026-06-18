# sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-gpt.c

Purpose: Freescale/NXP i.MX GPT driver supporting several hardware generations as both clocksource/sched_clock and one-shot clockevent.

Important APIs/types/functions: `enum imx_gpt_type` separates MX1, MX21, MX31, and MX6DL programming models; `struct imx_timer` holds MMIO, clocks, IRQ, variant ops, and `clock_event_device`; `struct imx_gpt_data` carries register offsets and callbacks. `mxc_clocksource_init()`, `mxc_clockevent_init()`, `_mxc_timer_init()`, and `mxc_timer_init_dt()` form the init path. Variant functions implement IRQ enable/disable/ack, TCTL setup, and next-event programming.

Control flow: DT match selects a variant, maps one GPT instance, gets IRQ and `ipg` plus `osc_per`/`per` clocks, enables clocks, resets control/prescaler, starts the GPT in free-running mode, registers the counter as clocksource/sched_clock, then registers and requests the clockevent IRQ. `set_next_event()` writes compare as current count plus delta and returns `-ETIME` if the target already passed. The ISR reads status, acknowledges through the variant callback, and invokes the event handler.

State/persistence: one static `initialized` gate permits one instance only. `sched_clock_reg` and optional ARM `delay_timer` point at the chosen counter for boot lifetime. No runtime persistence beyond MMIO register state and clockevent mode.

Dependencies/integration: many `TIMER_OF_DECLARE()` compatible strings for i.MX generations, CCF clocks, DT IRQ, ARM delay timer when enabled, clocksource/clockevents core.

Risks: variant-compatible quirks, legacy i.MX6Q/DL compatibility workaround, incomplete cleanup on some failure paths, single-instance assumption, and compare race sensitivity near min delta. Test signals are successful boot with expected compatible, stable sched_clock, clockevent one-shot tick, and no `-ETIME` storms under high interrupt load.

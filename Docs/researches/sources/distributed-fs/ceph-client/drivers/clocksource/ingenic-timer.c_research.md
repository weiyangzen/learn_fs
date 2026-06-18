# sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-timer.c

Purpose: provides clocksource, sched_clock, and one-shot per-CPU clockevent support using the Ingenic TCU MFD/regmap block on JZ47xx and X1000 SoCs. It reserves non-PWM TCU channels for CPU timers and one extra channel for a 16-bit clocksource.

Important APIs, types, and functions: `struct ingenic_tcu` stores the regmap, OF node, clocksource clock/channel, PWM channel mask, and flexible array of `struct ingenic_tcu_timer`. The clocksource path uses `ingenic_tcu_timer_read()` and `ingenic_tcu_clocksource_init()`. Clockevent operations are `ingenic_tcu_cevt_set_state_shutdown()`, `ingenic_tcu_cevt_set_next()`, `ingenic_tcu_cevt_cb()`, and `ingenic_tcu_setup_cevt()`. Power management is handled by `ingenic_tcu_suspend()` and `ingenic_tcu_resume()`.

Control flow: early OF timer declaration clears `OF_POPULATED`, obtains the syscon regmap, allocates per-possible-CPU timers, computes a PWM-reserved mask from DT, chooses the first free channels for CPU events and the next free channel for the clocksource, registers the clocksource, installs a dynamic CPU hotplug state to set up clockevents, and finally registers sched_clock. On each CPU online path the driver obtains the channel clock from the TCU clock provider, enables it, maps a child IRQ through the TCU IRQ domain, requests an IRQ, and registers a one-shot clockevent. The IRQ disables the channel and uses `smp_call_function_single_async()` to run the target CPU event handler.

State and persistence: runtime state lives in TCU channel registers, regmap, enabled clocks, IRQ mappings, and the global `ingenic_tcu` pointer. The PWM mask is read once during init and controls channel ownership. Suspend disables the clocksource clock and all online CPU timer clocks in noirq phase; resume re-enables them.

Dependencies and integration points: integrates with `linux/mfd/ingenic-tcu.h`, syscon/regmap, the TCU clock provider, the TCU IRQ domain, clockevents, clocksource, sched_clock, CPU hotplug, and PM noirq callbacks.

Risks: channel allocation is sensitive to `ingenic,pwm-channels-mask` and `num_possible_cpus()`. Clockevents are 16-bit and reject deltas above `0xffff`. The interrupt path targets `timer->cpu` asynchronously, so CPU hotplug and call-single data reuse must stay consistent. Test signals include successful boot on each compatible, free TCU channels left for PWM, hotplug online timer setup, one-shot tick delivery, suspend/resume without lost clocks, and no invalid mask messages.

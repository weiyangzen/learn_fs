# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-timer.c

Purpose: IP27 HUB real-time counter clocksource and per-CPU clockevent support.

Important APIs and control flow: `rt_next_event()` programs the slice-specific `PI_RT_COMPARE` register and reports late events. `hub_rt_counter_handler()` acknowledges the pending bit and calls the clockevent handler. `hub_rt_clock_event_init()` initializes a per-CPU one-shot clockevent at a fixed 800 ns cycle assumption. `hub_rt_clocksource_init()` registers a 52-bit continuous clocksource and sched_clock reader. `plat_time_init()` initializes source, global IRQ setup, and boot CPU event. `hub_rtc_init()` enables RT counters and clears pending state for the current node.

State, persistence, and integration: state includes per-CPU clockevent devices, names, HUB RT registers, and global clocksource. Dependencies include HUB timer IRQs, cputoslice/cputonasid mappings, and IRQ setup. Risks include hard-coded cycle time, cpuless-node skip behavior, and late-event handling under high interrupt latency. Test signals are registered `HUB-RT` clocksource, per-CPU `hub-rt` events, scheduler ticks, and no timer drift.

# sources/distributed-fs/ceph-client/drivers/clocksource/mips-gic-timer.c

Purpose: registers the MIPS GIC counter as a clocksource and sched_clock source where safe, and exposes the GIC compare interrupt as a percpu one-shot clockevent.

Important APIs, types, and functions: global state includes per-CPU `gic_clockevent_device`, `gic_timer_irq`, `gic_frequency`, `gic_count_width`, and `gic_clock_unstable`. Counter reads are handled by `gic_read_count_2x32()`, `gic_read_count_64()`, and `gic_hpt_read_multicluster()`. Event and hotplug paths are `gic_next_event()`, `gic_compare_interrupt()`, `gic_clockevent_cpu_init()`, `gic_starting_cpu()`, and `gic_dying_cpu()`. Clock-rate changes are watched by `gic_clk_notifier()`.

Control flow: OF init verifies a real MIPS GIC parent, obtains frequency from a clock or `clock-frequency`, parses the timer IRQ, initializes the clocksource with a mask derived from GIC count-width config, and requests the percpu compare IRQ. CPU startup clears `GIC_CONFIG_COUNTSTOP`, registers the local clockevent, and enables the IRQ. `set_next_event` writes either the local virtual processor compare register or a remote VP compare register. The ISR acknowledges by rewriting compare and dispatches the event handler.

State and persistence: state is in GIC count/compare registers, per-CPU clockevent objects, the clock notifier, and the unstable flag. Frequency changes update clockevents on all CPUs and mark the clocksource unstable.

Dependencies and integration points: integrates with MIPS CPS/CM/GIC accessors, CPU hotplug, percpu IRQs, clock notifiers, clocksource, clockevents, and VDSO clock mode selection. Multicluster systems use redirected counter reads and disable VDSO mode.

Risks: using sched_clock is restricted to stable-frequency or CM3+ cases and non-multicluster systems. Remote compare programming depends on `mips_cm_vp_id(cpu)`. Clock-rate changes make the clocksource unstable, so cpufreq behavior is central. Test signals include clean DT parent validation, working percpu timer IRQs on hotplug, stable reads on 32-bit and 64-bit counters, correct behavior under cpufreq, and expected VDSO clock mode.

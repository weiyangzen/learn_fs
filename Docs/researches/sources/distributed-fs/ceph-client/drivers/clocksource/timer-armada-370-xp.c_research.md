# sources/distributed-fs/ceph-client/drivers/clocksource/timer-armada-370-xp.c

Purpose: supports Marvell Armada 370, Armada 375, and Armada XP timers. A global timer 0 is used as a down-counting clocksource/sched_clock/delay timer, while local per-CPU timer 0 instances provide periodic and one-shot clockevents.

Important APIs, types, and functions: global state includes `timer_base`, `local_base`, `timer_clk`, `timer25Mhz`, `enable_mask`, `ticks_per_jiffy`, and per-CPU `armada_370_xp_evt`. Important paths are `local_timer_ctrl_clrset()`, `armada_370_xp_clkevt_next_event()`, `armada_370_xp_clkevt_shutdown()`, `armada_370_xp_clkevt_set_periodic()`, `armada_370_xp_timer_interrupt()`, hotplug callbacks, syscore suspend/resume callbacks, and compatible-specific init functions.

Control flow: compatible init chooses a clock source: Armada XP requires the fixed clock, Armada 375 prefers fixed but can fall back to divided SoC clock, Armada 370 uses divided SoC clock. Common init maps global and local register spaces, programs 25 MHz or divider mode, starts global timer 0 free-running, registers delay timer, sched_clock, and MMIO clocksource, allocates per-CPU clockevents, requests the percpu IRQ from interrupt index 4, installs CPU hotplug callbacks, and registers syscore ops. CPU startup configures local timer mode, registers the clockevent, and enables the percpu IRQ.

State and persistence: global state is singleton and SoC-mode dependent. Syscore suspend caches global and local control registers and resume reloads max values and restores controls. Per-CPU event state lives in allocated clockevent devices and local timer registers.

Dependencies and integration points: uses OF clocks/address/IRQ parsing, percpu IRQs, CPU hotplug, clocksource MMIO helpers, sched_clock, delay timer registration, syscore ops, and atomic MMIO modify helpers.

Risks: Armada XP must use the stable fixed timer to avoid cpufreq-sensitive timekeeping. Interrupt index and local/global register resources are DT-sensitive. Test signals include cpufreq stability on XP, per-CPU ticks through hotplug, delay timer registration, suspend/resume restoration, and correct fallback behavior on Armada 375.

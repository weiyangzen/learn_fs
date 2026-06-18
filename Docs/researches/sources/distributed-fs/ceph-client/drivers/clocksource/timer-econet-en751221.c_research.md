# sources/distributed-fs/ceph-client/drivers/clocksource/timer-econet-en751221.c

Purpose: supports EcoNet EN751221-style MIPS SoC high precision timers as a 32-bit MMIO clocksource/sched_clock and per-CPU one-shot clockevents. Each hardware block contains two timers, so the driver maps enough blocks for all possible CPUs.

Important APIs, types, and functions: `econet_timer` stores MMIO bases and frequency, and `econet_timer_pcpu` holds per-CPU clockevent devices. Register helpers are `reg_ctl()`, `reg_compare()`, `reg_count()`, `ctl_bit_enabled()`, and `ctl_bit_pending()`. Main paths are `cevt_interrupt()`, `cevt_set_next_event()`, `cevt_init_cpu()`, `sched_clock_read()`, `cevt_dev_init()`, `cevt_init()`, and `timer_init()`.

Control flow: DT init obtains the CPU timer clock, maps `DIV_ROUND_UP(num_possible_cpus(), 2)` register blocks, registers a clocksource on timer 0 count, initializes per-CPU events, and registers sched_clock. Event init maps the shared percpu IRQ, initializes all possible CPU timers with compare set to `U32_MAX`, fills per-CPU clockevent fields, and installs a CPU hotplug state. CPU startup enables the appropriate timer bit, enables the percpu IRQ, and registers the clockevent. The ISR verifies that the current CPU timer is pending, writes compare to current count to clear/neutralize, and calls the handler.

State and persistence: state is static and marked `__ro_after_init` for bases/frequency. Per-CPU devices are permanent. Hardware compare/count/control bits hold event state.

Dependencies and integration points: integrates with OF clocks/address/IRQ, percpu IRQs, CPU hotplug, clocksource MMIO helper, clockevents, and sched_clock.

Risks: the number of mapped blocks depends on possible CPUs and two timers per block. `cevt_set_next_event()` rejects too-close deadlines using signed arithmetic and the minimum delta. Test signals include correct block mapping on 1- and 2-block SoCs, per-CPU pending checks, CPU hotplug setup, stable timer 0 clocksource, and `-ETIME` handling for close deadlines.

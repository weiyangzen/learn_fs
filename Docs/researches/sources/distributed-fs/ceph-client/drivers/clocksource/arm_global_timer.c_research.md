# sources/distributed-fs/ceph-client/drivers/clocksource/arm_global_timer.c

Purpose: registers the ARM Cortex-A9 global timer as a 64-bit clocksource, sched_clock/delay timer, and per-CPU clockevent source.

Important APIs/types/functions: `_gt_counter_read()`, `gt_compare_set()`, `gt_clocksource_init()`, clockevent callbacks, clock-rate notifier `gt_clk_rate_change_cb()`, CPU hotplug callbacks, and `global_timer_of_register()`.

Control flow: DT init validates CPU revision, maps registers, enables the parent clock, computes a prescaler, registers a clock notifier, allocates per-CPU clockevents, requests PPI, initializes the clocksource, installs CPU hotplug state, and registers delay timer support.

State and persistence: global MMIO base, target rate, prescaler bookkeeping, PPI, clock notifier, and per-CPU clockevent objects persist. Hardware counter is reset and enabled during clocksource init.

Dependencies and integration points: depends on OF, CCF clock rate notifications, ARM CPU ID checks, per-CPU IRQs, sched_clock, delay timer registration, and clockevents.

Risks: older Cortex-A9 revisions are rejected. Clock-rate changes are accepted only if a prescaler can preserve target rate within error bounds. Erratum 740657 requires special oneshot interrupt handling. Resource cleanup exists only for init failures.

Test signals: Zynq and AM43 prescaler defaults, CPU hotplug, parent clock-rate transitions, oneshot duplicate-interrupt workaround, and sched_clock monotonicity.

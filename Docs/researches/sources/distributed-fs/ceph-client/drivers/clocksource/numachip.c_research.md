# sources/distributed-fs/ceph-client/drivers/clocksource/numachip.c

Purpose: registers the Numascale NumaChip2 local CSR timer as an x86 64-bit clocksource and per-CPU one-shot clockevent.

Important APIs, types, and functions: per-CPU `numachip2_ced`, `numachip2_clocksource`, and `numachip2_clockevent` define the clocksource/event devices. `numachip2_timer_read()` reads `NUMACHIP2_TIMER_NOW`; `numachip2_set_next_event()` writes a relative deadline; `numachip_timer_interrupt()` dispatches the platform IPI callback; `numachip_timer_each()` configures each CPU; and `numachip_timer_init()` is the arch initcall.

Control flow: at `arch_initcall`, the driver exits unless `numachip_system == 2`. It resets the timer, registers a 1 GHz-equivalent clocksource with identity mult/shift, installs `x86_platform_ipi_callback`, and schedules `numachip_timer_each()` on every CPU. Each CPU configures the timer interrupt CSR with platform IPI vector and local APIC ID, copies the static clockevent template, sets cpumask, and registers the clockevent.

State and persistence: state lives in NumaChip local CSR registers and per-CPU `clock_event_device` structs. There is no suspend, remove, or persistent storage handling in this file.

Dependencies and integration points: tightly integrated with x86 APIC/IPI plumbing, NumaChip CSR accessors, `numachip_system`, and the clockevents/clocksource core.

Risks: the interrupt routing word encodes local APIC ID and `X86_PLATFORM_IPI_VECTOR`; mistakes break per-CPU event delivery. The clocksource uses fixed mult/shift and `NSEC_PER_SEC` registration, assuming hardware units match nanosecond ticks. Test signals include detection only on NumaChip2 systems, clocksource registration as `numachip2`, per-CPU clockevents registered on all CPUs, and timer IPIs invoking event handlers.

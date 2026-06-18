# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-32k.c

## Purpose

`timer-ti-32k.c` registers the OMAP/TI 32 kHz synchronized counter as a continuous clocksource and sched_clock. It provides low-power timekeeping on OMAP-class systems and influences DMTimer system-timer selection.

## APIs And Flow

`struct ti_32k` stores the mapped base, selected counter register, and `struct clocksource`. `ti_32k_timer_init()` maps the node, marks the source suspend-nonstop except on AM43, optionally enables `ti,sysc` parent `fck` and `ick`, selects legacy or highlander counter offset by revision scheme bits, registers `32k_counter` at 32768 Hz, and registers sched_clock.

## State, Dependencies, Risks, Tests

State is static in `ti_32k_timer`; the hardware owns the free-running counter. Dependencies include OF mapping, OF clock lookup, common clocks, clocksource, sched_clock, and `ti,sysc` parent conventions. Risks are wrong revision offset selection, missing parent clocks, AM43 suspend behavior, and inconsistent early module clock handling. Test boot logs, sched_clock registration, suspend/resume timekeeping, and DMTimer fallback when this node is disabled.

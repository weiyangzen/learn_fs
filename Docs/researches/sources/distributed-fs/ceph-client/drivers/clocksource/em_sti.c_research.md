# sources/distributed-fs/ceph-client/drivers/clocksource/em_sti.c

Purpose: supports the Renesas Emma Mobile STI 48-bit timer as both a clocksource and a oneshot clockevent.

Important APIs/types/functions: `struct em_sti_priv`, `em_sti_enable()/disable()`, `em_sti_count()`, `em_sti_set_next()`, clocksource enable/disable callbacks, clockevent callbacks, `em_sti_probe()`, and module init/exit.

Control flow: platform probe allocates private state, maps MMIO, requests IRQ, prepares/enables the `sclk` to determine rate, initializes a raw spinlock, then registers clockevent and clocksource. The timer clock is enabled lazily while either user is active.

State and persistence: private device state tracks active users for clocksource and clockevent, clock rate, MMIO base, clock handle, and embedded CCF objects. Counter and compare state is in hardware.

Dependencies and integration points: platform driver with OF compatible `renesas,em-sti`; depends on devm resources, CCF, raw spinlocks, IRQ, clocksource, and clockevents.

Risks: `em_sti_enable()` resets the counter when first user starts, which can affect continuity if users transition unexpectedly. Next-event returns failure when the compare value is already too close. Interrupt handler does not explicitly clear status; compare programming clears sources.

Test signals: platform probe, clocksource enable/disable suspend/resume hooks, oneshot event latency, shared clocksource/clockevent active-user transitions, and 48-bit read ordering.

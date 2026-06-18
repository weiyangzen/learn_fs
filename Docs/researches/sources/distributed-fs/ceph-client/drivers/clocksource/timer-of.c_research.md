# sources/distributed-fs/ceph-client/drivers/clocksource/timer-of.c

Purpose: shared helper for early device-tree timer drivers to acquire MMIO base, clock, and IRQ resources into a `struct timer_of`.

Important APIs/types/functions: `timer_of_init()` is the main exported init helper; `timer_of_cleanup()` releases resources. Internal helpers initialize and exit IRQ (`timer_of_irq_init/exit`), clock (`timer_of_clk_init/exit`), and base (`timer_of_base_init/exit`) resources.

Control flow: `timer_of_init()` checks flags in order: map base, enable/get clock and rate/period, request IRQ, then assigns a default clockevent name and stores the DT node. On failure it unwinds only resources acquired so far. IRQ acquisition prefers named IRQ then index; clock acquisition prefers named clock then index; base mapping uses `of_io_request_and_map()` when a name is supplied, otherwise `of_iomap()`.

State/persistence: it writes resource pointers, rate, period, IRQ number, and `np` into caller-owned `timer_of`. No global state. Resources are intended to persist for boot-lifetime timer users unless `timer_of_cleanup()` is called on init failure.

Dependencies/integration: DT OF address/IRQ/clock APIs, CCF, `request_irq()`, `clock_event_device`, and `timer-of.h` struct layout.

Risks: `timer_of_irq_exit()` frees IRQ using `to->clkevt`; callers must not mutate clkevt unexpectedly before cleanup. `timer_of_base_exit()` calls `iounmap()` even for regions mapped with request-and-map, so ownership expectations matter. It is `__init`, so runtime users should not call it. Tests are indirect: drivers using base/clock/IRQ combinations should fail cleanly on missing resources and not leak on early init errors.

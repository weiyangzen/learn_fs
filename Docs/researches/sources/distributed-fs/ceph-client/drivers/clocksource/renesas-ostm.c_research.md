# sources/distributed-fs/ceph-client/drivers/clocksource/renesas-ostm.c

Purpose: supports Renesas OSTM channels. The first probed channel becomes a free-running 32-bit clocksource and sched_clock; later channels become periodic/one-shot clockevents.

Important APIs, types, and functions: the file uses `struct timer_of` for MMIO, clock, and IRQ resources. Important functions are `ostm_timer_stop()`, `ostm_init_clksrc()`, `ostm_init_sched_clock()`, `ostm_clock_event_next()`, `ostm_shutdown()`, `ostm_set_periodic()`, `ostm_set_oneshot()`, `ostm_timer_interrupt()`, `ostm_init_clkevt()`, and `ostm_init()`.

Control flow: OF timer declaration and the built-in platform driver both call `ostm_init()`. It allocates `timer_of`, deasserts an optional reset, selects flags for base/clock and optionally IRQ depending on whether `system_clock` is already set, initializes resources with `timer_of_init()`, and branches by first-vs-later channel. The clocksource path stops the timer, writes free-run mode, starts it, registers an up-counting MMIO clocksource, and stores the sched_clock base. The event path configures callbacks and registers the clockevent. In oneshot interrupts, the channel is stopped before dispatching the event handler.

State and persistence: `system_clock` is the global selector and sched_clock base, so probe order determines channel role. Reset control is deasserted at init and asserted on failure. Hardware counter, compare, enable, and mode registers hold runtime state.

Dependencies and integration points: depends on `timer-of.h`, OF/platform probing, reset control, clocksource MMIO helper, clockevents, sched_clock, and IRQ handling. It marks nodes populated after successful setup.

Risks: first-probed-channel semantics make DT ordering important. `ostm_timer_stop()` busy-waits for `TE` to clear, so hardware bus faults can hang early boot. Periodic compare uses `timer_of_period(to) - 1`. Test signals include one channel used for clocksource, second for events, reset deassert/assert behavior, periodic and oneshot ticks, and clean platform-driver reprobe behavior.

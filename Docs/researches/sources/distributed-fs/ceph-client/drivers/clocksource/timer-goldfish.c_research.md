# sources/distributed-fs/ceph-client/drivers/clocksource/timer-goldfish.c

Purpose: supports the Goldfish emulator timer as a combined clocksource and one-shot clockevent. It is used by virtual/emulated platforms rather than physical SoC timer blocks.

Important APIs, types, and functions: `struct goldfish_timer` stores MMIO base, clockevent, and clocksource. Helpers convert from clockevent/clocksource to the container. Important routines are `goldfish_timer_read()`, `goldfish_timer_set_oneshot()`, `goldfish_timer_shutdown()`, `goldfish_timer_next_event()`, `goldfish_timer_irq()`, and `goldfish_timer_init()`.

Control flow: initialization receives IRQ and base from architecture/platform code, allocates state, fills the clocksource and clockevent devices, requests the IRQ, registers the source, and registers the one-shot event device. Clocksource reads combine the timer's high/low registers to return current virtual time. Next-event programming writes the target time or alarm registers based on current counter plus delta. The IRQ clears/acknowledges the device and calls the event handler.

State and persistence: state is heap allocated and tied to the emulator timer MMIO region. The timer device maintains current time and alarm state. No persistent storage exists.

Dependencies and integration points: integrates with the Goldfish platform timer device, MMIO accessors, IRQ core, clocksource, and clockevents. It is typically wired by architecture setup rather than a DT `TIMER_OF_DECLARE()` in this file.

Risks: emulator register ordering and 64-bit read consistency determine monotonicity. Alarm programming must handle very small deltas and shutdown must prevent stale interrupts. Test signals include boot in Goldfish-based emulator, monotonic virtual clocksource reads, one-shot alarm delivery, no stale IRQ after shutdown, and correct behavior under VM pause/resume.

# sources/distributed-fs/ceph-client/drivers/clocksource/timer-vt8500.c

## Purpose

`timer-vt8500.c` registers the VIA/WonderMedia VT8500 3 MHz timer as both clocksource and CPU0 one-shot clockevent.

## APIs And Flow

Global `regbase` holds the mapping. `vt8500_timer_read()` triggers and waits for a counter read. `vt8500_timer_set_next_event()` writes an absolute match based on the current clocksource plus cycles, rejects too-near deadlines, and enables interrupts. `vt8500_shutdown()` disables interrupts, and the ISR clears status then calls the event handler. Init maps MMIO and IRQ, initializes control/status/match registers, registers the clocksource, requests IRQ, and registers the clockevent.

## State, Dependencies, Risks, Tests

Static clocksource/clockevent objects and hardware registers hold all state. Dependencies include OF address/IRQ parsing, clocksource, clockevents, IRQ handling, delay calibration, and MMIO. Risks include silent access-status timeout, near-deadline `-ETIME`, fixed 3 MHz rate, no SMP/per-CPU handling, and partial-init cleanup gaps. Test clocksource/clockevent registration, oneshot timer workloads, shutdown behavior, and interrupt latency edge cases.

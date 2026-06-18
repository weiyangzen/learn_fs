# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ralink.c

Purpose: Ralink RT3352/MT7620 system tick counter driver providing a 16-bit MMIO clocksource and a higher-rated one-shot clockevent.

Important APIs/types/functions: `struct systick_device` stores membase, clockevent, IRQ request flag, and scale. `systick_next_event()` programs compare modulo `SYSTICK_FREQ`. `systick_set_oneshot()` lazily requests IRQ and enables external systick routing/counter; `systick_shutdown()` frees IRQ and disables config.

Control flow: init maps MMIO, manually calculates clockevent mult/shift/delta bounds for fixed 50 kHz, parses IRQ, registers MMIO clocksource, then registers the clockevent device. The IRQ handler simply dispatches the event handler. Shutdown tears down the IRQ, so re-entering oneshot will request it again.

State/persistence: static `systick` object holds all driver state. `irq_requested` tracks dynamic IRQ ownership.

Dependencies/integration: compatible `ralink,cevt-systick`, fixed `SYSTICK_FREQ`, MIPS IRQ routing comment, clocksource/clockevents.

Risks: no explicit interrupt acknowledge in handler; dynamic request/free from clockevent state transitions can fail and still sets `irq_requested = 1`; modulo compare on 50k range limits deltas; typo comment aside, event handler default is a no-op until core replaces it. Tests should verify IRQ routing to MIPS IRQ7, oneshot reactivation, compare wrap, and source registration at rating 301.

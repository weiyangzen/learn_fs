# sources/distributed-fs/ceph-client/drivers/clocksource/timer-cs5535.c

Purpose: registers a CS5535/CS5536 MFGPT timer as a clockevent device using the 32.768 kHz input divided by 16. It is a clockevent-only driver, not a clocksource.

Important APIs, types, and functions: global `cs5535_event_clock` holds the allocated MFGPT timer. The operations are `disable_timer()`, `start_timer()`, `mfgpt_shutdown()`, `mfgpt_set_periodic()`, `mfgpt_next_event()`, `mfgpt_tick()`, and `cs5535_mfgpt_init()`. A module parameter `irq` can select the MFGPT IRQ.

Control flow: module init allocates any working-domain MFGPT timer, configures the CMP2 IRQ, requests a shared timer IRQ, writes the clock scale and CMP2 event mode into the setup register, and registers a periodic/one-shot clockevent at `MFGPT_HZ`. Starting an event writes CMP2, clears the counter, and enables count/CMP2. The IRQ checks whether the event came from this timer, disables and clears it, restarts it for periodic mode, and dispatches the event handler.

State and persistence: state is singleton and module-global. Hardware state lives in MFGPT setup, compare, and counter registers. There is no disk persistence; cleanup paths only exist for init failure.

Dependencies and integration points: integrates with the CS5535 MFGPT allocation/IRQ API, Linux module parameters, shared IRQ handling, and clockevents.

Risks: the handler must distinguish shared IRQs correctly. `disable_timer()` clears compare conditions unconditionally to avoid races, so changes must preserve CMP clear behavior. The selected divisor fixes min/max delta behavior. Test signals include module load on CS5535/CS5536, chosen IRQ logged, periodic and oneshot tick delivery, correct `IRQ_NONE` for unrelated shared interrupts, and clean failure if no MFGPT is available.

# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sprd.c

Purpose: Spreadtrum timer driver with one clockevent timer and a separate suspend-nonstop 64-bit clocksource.

Important APIs/types/functions: static `timer_of to` for events and `suspend_to` for persistent source. Event helpers enable/disable/update counter/interrupt and callbacks implement periodic, shutdown, and next-event. `sprd_suspend_timer_read()` reads shadow high/low/high and inverts for a down-counter-style source.

Control flow: `sprd_timer_init()` initializes base/clock/IRQ, enables interrupt, and registers a periodic/oneshot dynamic clockevent. Interrupt clears flag, disables timer for oneshot, and dispatches. `sprd_suspend_timer_init()` initializes a base/clock-only timer and registers `suspend_clocksource`; enable loads max 64-bit value and starts periodic 64-bit mode.

State/persistence: two static `timer_of` structures and one static clocksource. The suspend timer can continue through suspend by clocksource flags.

Dependencies/integration: compatibles `sprd,sc9860-timer` and `sprd,sc9860-suspend-timer`, `timer-of`, clocksource/clockevents.

Risks: event `set_state_oneshot` is not explicitly supplied, relying on `set_next_event`; suspend source read assumes shadow register protocol; `sprd_timer_enable_interrupt()` writes only enable bit and may clear other status depending on hardware semantics. Test signals include both DT nodes, suspend clocksource selection, one-shot disable after interrupt, 64-bit shadow read consistency, and periodic events.

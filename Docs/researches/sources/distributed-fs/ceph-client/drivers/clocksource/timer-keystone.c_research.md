# sources/distributed-fs/ceph-client/drivers/clocksource/timer-keystone.c

Purpose: TI Keystone broadcast clockevent driver for a 64-bit timer block. It does not register a clocksource.

Important APIs/types/functions: static `timer` holds MMIO base, HZ period, and `clock_event_device`. `keystone_timer_config()` disables the timer, resets counters, writes 64-bit period registers, and re-enables in one-shot or periodic mode with explicit I/O barriers. `keystone_set_next_event()`, `keystone_shutdown()`, and `keystone_set_periodic()` implement clockevent callbacks.

Control flow: `keystone_timer_init()` parses IRQ and base, enables the input clock, disables and resets the hardware, unresets the 64-bit timer, initializes counters, enables timer interrupt generation, requests IRQ, fills the clockevent structure, and registers it. IRQ dispatch is simple because hardware interrupt enable/status was configured globally.

State/persistence: a single static `timer` persists for boot lifetime. `hz_period` is derived from the enabled clock rate. Hardware mode/counter registers store runtime state.

Dependencies/integration: compatible `ti,keystone-timer`, one clock, one IRQ, clockevents core. Uses `__iowmb()` because relaxed MMIO calls are intentionally paired with explicit ordering.

Risks: global singleton, no cleanup for clocksource because none exists, limited error unwinding after `request_irq()` failure, and correctness depends on barriers around disable/write/enable sequence. Test signals include periodic and one-shot clockevent modes, IRQ delivery, clock rate log, and suspend/idle interactions when used as a broadcast event source.

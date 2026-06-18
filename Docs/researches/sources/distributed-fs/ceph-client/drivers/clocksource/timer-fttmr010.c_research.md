# sources/distributed-fs/ceph-client/drivers/clocksource/timer-fttmr010.c

Purpose: supports Faraday FTTMR010-compatible timers and Aspeed AST2400/2500/2600 variants. It uses one timer as clocksource/sched_clock/delay timer and another as periodic/one-shot clockevent, with variant-specific control-bit layouts and interrupt clearing.

Important APIs, types, and functions: `struct fttmr010` stores base, clock rate, tick values, control masks, interrupt masks, endian/counter direction choices, and embedded clockevent. Main functions are the up/down current-timer and sched_clock readers, `fttmr010_timer_set_next_event()`, `fttmr010_timer_shutdown()`, `ast2600_timer_shutdown()`, `fttmr010_timer_set_oneshot()`, `fttmr010_timer_set_periodic()`, `fttmr010_timer_interrupt()`, `ast2600_timer_interrupt()`, `fttmr010_common_init()`, and the compatible-specific init wrappers.

Control flow: compatible-specific `TIMER_OF_DECLARE()` selects standard Faraday/Gemini/Moxart, Aspeed, or AST2600 initialization. Common init maps MMIO, obtains clock and IRQ, configures the clocksource timer with max load/match values and direction, registers sched_clock/clocksource/delay timer, initializes the clockevent timer, requests IRQ, and registers clockevents. Event programming writes load/match registers and enables interrupt/counter bits. AST2600 uses separate clear registers and different shutdown semantics.

State and persistence: runtime state is global through `local_fttmr`, clockevent data, hardware count/load/match/control/interrupt registers, and delay timer registration. There is no disk persistence.

Dependencies and integration points: integrates with OF clocks/address/IRQ, `clocksource_mmio_init()` or custom readers depending on direction, sched_clock, clockevents, current timer delay, and Aspeed/Faraday-compatible register layouts.

Risks: register control-bit positions differ between generic and Aspeed hardware; AST2600 has a distinct clear register. Counter direction affects read inversion and delay timer behavior. Test signals include all compatible variants, interrupt acknowledgement paths, periodic and oneshot event delivery, monotonic source reads, and delay timer calibration.

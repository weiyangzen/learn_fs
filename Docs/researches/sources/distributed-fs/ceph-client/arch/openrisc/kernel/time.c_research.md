<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/time.c

## Purpose
Implements OpenRISC tick timer as a clocksource, per-CPU one-shot clockevent, and timer interrupt source.

## Important APIs, Types, And Functions
`openrisc_timer_set()`, `openrisc_timer_set_next()`, `openrisc_clockevent_init()`, `timer_interrupt()`, `openrisc_timer_read()`, `openrisc_timer_init()`, and `time_init()` are central. Per-CPU `clockevent_openrisc_timer` stores clockevent devices.

## Control Flow
`time_init()` verifies tick timer presence, registers a 32-bit continuous clocksource, initializes current CPU clockevent, initializes OF clocks, and probes timers. Timer interrupts acknowledge TTMR, enter IRQ context, invoke the clockevent handler, and exit.

## State And Persistence
Programs TTCR/TTMR SPRs and per-CPU clockevent state. Clocksource registration persists globally.

## Dependencies And Integration Points
Depends on `cpuinfo_or1k` clock frequency, clocksource/clockevents core, IRQ handling, OF clock init, and SMP broadcast support.

## Risks
Compare period uses only low 28 bits. Systems without TTMR panic. Timer ack disables interrupt bits while keeping continuous mode, so next-event programming must follow correctly.

## Test Signals
Clocksource registration, high-resolution timer behavior, scheduler ticks, SMP clockevent setup, and boot panic on no tick timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/time.c -->

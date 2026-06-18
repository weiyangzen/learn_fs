<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/time.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/time.h

## Purpose
Declares OpenRISC timer and SMP cycle-counter synchronization hooks.

## Important APIs, Types, And Functions
Exports `openrisc_clockevent_init()`, `openrisc_timer_set()`, `openrisc_timer_set_next()`, and, under SMP, `synchronise_count_master()` and `synchronise_count_slave()`.

## Control Flow
`time_init()` and secondary CPU startup call clockevent initialization; timer interrupt setup calls the set-next-event path; SMP bring-up synchronizes TTCR counters.

## State And Persistence
The functions manipulate per-CPU tick timer SPRs and per-CPU clockevent state.

## Dependencies And Integration Points
Implemented by `kernel/time.c` and `kernel/sync-timer.c`. Integrated with clocksource, clockevents, IRQ, and SMP boot.

## Risks
Timer APIs assume the OpenRISC tick timer exists and has a 28-bit compare period. Wrong ordering can miss clock events or desynchronize SMP sched clocks.

## Test Signals
Boot without timer should panic; normal boot should register clocksource/clockevent, deliver periodic scheduler ticks, and sync CPU counters during SMP startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/time.h -->

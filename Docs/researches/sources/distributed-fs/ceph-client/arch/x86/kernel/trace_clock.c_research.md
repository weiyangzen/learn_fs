# sources/distributed-fs/ceph-client/arch/x86/kernel/trace_clock.c

## Purpose
`trace_clock.c` implements the x86 TSC trace clock, returning raw ordered cycle counts for tracing.

## Important APIs, Types, And Functions
The sole function is `u64 notrace trace_clock_x86_tsc(void)`, which returns `rdtsc_ordered()`.

## Control Flow
There is no branching; the clock reads the ordered TSC and returns it.

## State, Persistence, Dependencies, Integration
No state is modified. It depends on x86 TSC helpers and ordering semantics. The tracing subsystem can select this clock through registration elsewhere; consumers must treat the unit as cycles, not nanoseconds.

## Risks And Test Signals
TSC stability and cross-CPU synchronization affect interpretation. `notrace` avoids recursion. Test trace-clock selection, monotonic-enough timestamps on intended systems, no tracing recursion, and correct cycle-unit display.

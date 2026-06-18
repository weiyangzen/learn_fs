# sources/distributed-fs/ceph-client/include/linux/irqflags_types.h

## Purpose
`irqflags_types.h` isolates per-task IRQ trace event storage used when IRQ flag tracing is enabled.

## Important APIs, types, and functions
Under `CONFIG_TRACE_IRQFLAGS`, it defines `struct irqtrace_events` with counters, instruction pointers, and event IDs for hardirq and softirq enable/disable transitions.

## Control flow
The tracing/lockdep infrastructure updates this structure when IRQ state transitions occur, allowing diagnostics to report where IRQs were enabled or disabled.

## State and persistence
State is per-task runtime diagnostic metadata. It is not persistent.

## Dependencies and integration points
It is consumed by task structures and `irqflags.h` tracing paths.

## Risks and test signals
Risks include stale IP/event tracking and missing compile coverage when tracing is disabled. Tests should cover lockdep reports under IRQ misuse and both tracing-enabled and disabled builds.

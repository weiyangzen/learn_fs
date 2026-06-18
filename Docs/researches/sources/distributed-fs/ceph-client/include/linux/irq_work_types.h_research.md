# sources/distributed-fs/ceph-client/include/linux/irq_work_types.h

## Purpose
`irq_work_types.h` isolates the `struct irq_work` layout so low-level headers can use the type without pulling in full IRQ work APIs.

## Important APIs, types, and functions
It defines `struct irq_work` with a `struct __call_single_node`, callback function pointer, and `struct rcuwait`.

## Control flow
There are no functions. Other headers initialize, queue, inspect, and synchronize this structure.

## State and persistence
State is per-work-item runtime state encoded in call-single flags and wait state. Nothing persists.

## Dependencies and integration points
It depends on SMP call-single types and generic integer types, and is consumed by `irq_work.h`, tracing, scheduler, and RCU-adjacent code.

## Risks and test signals
Risks are ABI/layout assumptions by low-level code and improper zeroing or copying of live work items. Tests should focus on initialization macros, sync behavior, and compile coverage in architecture headers.

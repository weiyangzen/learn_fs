# sources/distributed-fs/ceph-client/kernel/irq/debug.h

## Purpose
`debug.h` provides a small internal diagnostic helper for printing an IRQ descriptor to the kernel log. It is included by `internals.h` for use in bad/spurious IRQ paths.

## Important APIs, types, and functions
The only function is `print_irq_desc(unsigned int irq, struct irq_desc *desc)`. It uses local macros to print selected descriptor status flags and internal state bits, and a static ratelimit state to avoid flooding.

## Control flow
When called, the helper checks its ratelimit, prints the IRQ number, descriptor pointer, depth, counts, flow handler pointer, chip pointer, action/handler pointer, and selected `_IRQ_*` and `IRQS_*` bits.

## State and persistence
The helper has only a static ratelimit state. It reads descriptor fields but does not mutate them.

## Dependencies and integration points
It depends on `struct irq_desc`, internal `IRQS_*` definitions, and printk symbol formatting. It is used by `handle_bad_irq()` and dummy chip bad-ack paths to aid debugging of illegal or unhandled interrupts.

## Risks and test signals
Risks include printing stale or partially updated descriptor state if called without appropriate locking, incomplete bit coverage due to the disabled `___PD` macro, and rate limiting hiding repeated issues. Test signals include bad IRQ injection, spurious IRQ reports, and verifying output includes chip/action symbols without log flooding.

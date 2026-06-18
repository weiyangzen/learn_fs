# sources/distributed-fs/ceph-client/include/linux/irqhandler.h

## Purpose
`irqhandler.h` breaks include cycles by defining the interrupt flow-handler function type used by IRQ descriptors and chips.

## Important APIs, types, and functions
It forward-declares `struct irq_desc` and defines `typedef void (*irq_flow_handler_t)(struct irq_desc *desc)`.

## Control flow
IRQ descriptors store an `irq_flow_handler_t`; dispatch code invokes it to implement level, edge, fasteoi, percpu, nested, or bad interrupt flow.

## State and persistence
The header has no state.

## Dependencies and integration points
It is included by `irq.h`, `irqdomain.h`, `irqdesc.h`, and irqchip drivers to avoid circular dependencies.

## Risks and test signals
Risks are limited to function-signature mismatches and invalid descriptors passed to handlers. Compile coverage across IRQ headers and runtime dispatch tests for each flow handler are sufficient signals.

# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-sa11x0.h

## Purpose
`irq-sa11x0.h` declares legacy SA-11x0 interrupt initialization for non-DT platforms.

## Important APIs, types, and functions
It declares `sa11x0_init_irq_nodt(int irq_start, resource_size_t io_start)`.

## Control flow
Platform code calls the init function with an IRQ base and MMIO start address so the SA-11x0 interrupt controller can initialize descriptors and hardware.

## State and persistence
State is hardware register configuration and generic IRQ descriptor mappings established by the implementation.

## Dependencies and integration points
It integrates ARM SA-11x0 board files with generic IRQ handling and low-level MMIO resources.

## Risks and test signals
Risks include wrong IO start address, IRQ base collisions, and missing legacy init. Tests should boot SA-11x0 board configurations and trigger each interrupt source.

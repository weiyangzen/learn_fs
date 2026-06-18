# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-vic.h

## Purpose
`arm-vic.h` declares legacy ARM VIC initialization for non-DT or early platform code.

## Important APIs, types, and functions
It declares `vic_init(void __iomem *base, unsigned int irq_start, u32 vic_sources, u32 resume_sources)`.

## Control flow
Board code maps the VIC base, chooses the Linux IRQ base and source masks, then calls `vic_init` to register and configure the controller.

## State and persistence
State is in hardware registers and generic IRQ descriptors initialized by the VIC implementation. Resume source state supports PM restoration.

## Dependencies and integration points
It depends on MMIO types and integrates legacy ARM platforms with generic IRQ descriptors.

## Risks and test signals
Risks include wrong MMIO base, IRQ range collisions, and resume-source mask mistakes. Tests should boot legacy VIC boards and exercise suspend/resume and each IRQ source.

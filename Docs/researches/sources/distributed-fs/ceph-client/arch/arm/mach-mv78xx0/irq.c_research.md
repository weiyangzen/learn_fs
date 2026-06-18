# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/irq.c

Purpose: MV78xx0 interrupt-controller setup.

Important APIs/types/functions: Defines IRQ initialization and mask/unmask/chained handling helpers for MV78xx0 interrupt registers.

Control flow: Init maps/uses bridge interrupt registers, configures irq chips/domains or legacy descriptors, masks/unmasks sources, and dispatches pending interrupts.

State and persistence: Hardware state is interrupt mask/cause registers; software state is irq chip data/descriptor setup.

Dependencies and integration points: Depends on `irqs.h`, bridge regs, ARM irq core, and machine init.

Risks: Wrong mask/cause handling loses interrupts or causes storms. Legacy IRQ numbering must match board resources.

Test signals: Boot and exercise timer, GPIO, Ethernet, SATA, and PCIe interrupts.

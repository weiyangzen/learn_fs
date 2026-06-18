# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/irq.h

Purpose: Declares the Orion legacy interrupt controller initialization API.

Important API: `orion_irq_init(unsigned int irq_start, void __iomem *maskaddr)` initializes a 32-bit mask-register interrupt block starting at `irq_start`.

Control flow/state/dependencies: The implementation masks all interrupts and registers a generic irq chip over the MMIO mask register. Callers supply the IRQ base and mapped mask register during platform initialization. Depends on Linux IRQ and `__iomem` types.

Risks and tests: Incorrect `irq_start` or `maskaddr` will misroute or fail all platform interrupts. Boot tests should verify parent interrupt delivery, initial masking, and expected IRQ numbering for machines using this header.

# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/irq.c

Purpose: BCM63xx interrupt controller setup and dispatch for internal and external IRQ lines, including CPU-family-specific IPIC/EPIC register widths.

Important APIs and functions: generated IPIC helpers provide internal IRQ mask/unmask and dispatch variants. `plat_irq_dispatch()` decodes MIPS pending interrupt bits and routes timer, internal, and external interrupts. `bcm63xx_internal_irq_mask/unmask()` and external counterparts update controller registers under spinlocks. `bcm63xx_init_irq()` installs irq_chip handlers. `arch_init_irq()` initializes MIPS CPU IRQs and BCM63xx controller state.

Control flow: architecture IRQ init selects the correct dispatch/mask implementations, configures each IRQ descriptor, and unmasks CPU-level interrupt lines. Runtime dispatch reads pending status and calls generic IRQ handling for active bits.

State and persistence: maintains mask state in interrupt controller registers and spinlock-protected updates. No storage survives reset.

Dependencies and integration points: integrates MIPS CPU interrupt lines, BCM63xx PERF/IRQ registers, generic IRQ core, SMP affinity conditionals, and platform-device IRQ resources.

Risks and test signals: wrong width, pending-bit mapping, or external IRQ clear behavior can lose or storm interrupts. Test signals include timer ticks, UART/Ethernet/SPI interrupts, external GPIO IRQs, `/proc/interrupts`, SMP affinity behavior where supported, and no spurious interrupt floods.

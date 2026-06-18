# sources/distributed-fs/ceph-client/arch/arm/plat-orion/irq.c

Purpose: Initializes a simple 32-line Marvell Orion interrupt mask controller using Linux generic irq-chip infrastructure.

Important API/function: `orion_irq_init()` masks all interrupts by writing zero to the provided mask register, allocates a generic chip named `orion_irq`, assigns clear-bit mask and set-bit unmask operations, and registers 32 level-triggered IRQs starting at `irq_start`.

Control flow/state: Called during early platform interrupt setup. Hardware mask register state persists; generic irq-chip mask cache is initialized from the all-masked state. There are no per-file static globals.

Dependencies/integration: Uses Linux IRQ, irqdomain, MMIO, and generic-chip APIs. Includes GPIO and OF headers although this file only needs the core IRQ path. Board/machine code supplies mapped `maskaddr`.

Risks/tests: The function assumes one 32-bit mask register and level-triggered lines. Invalid `irq_start`, wrong register mapping, or SoCs with split/more lines need different setup. Tests should verify all interrupts start masked, unmask/mask writes update the hardware bit as expected, and IRQ handlers fire on each platform line.

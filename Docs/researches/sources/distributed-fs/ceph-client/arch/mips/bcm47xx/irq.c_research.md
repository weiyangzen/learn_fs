## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/irq.c

Purpose: implements BCM47XX CPU interrupt dispatch and initialization, including BCMA-specific timer interrupt routing and optional MIPS vectored interrupt setup.

Important APIs and functions: `plat_irq_dispatch()` reads CP0 cause/status, masks to pending interrupt bits, clears those bits from CP0 status, and calls `do_IRQ()` for IP7, then IP2 through IP6. `arch_init_irq()` completes bus setup through `bcm47xx_bus_setup()`, applies BCMA MIPS74K interrupt mask and `cp0_compare_irq` fixup when needed, initializes CPU IRQs, and installs vectored handlers if `cpu_has_vint`. Macro `DEFINE_HWx_IRQDISPATCH()` creates simple handlers for hardware IRQs 2 through 7.

Control flow: architecture IRQ init is the first callback after `mm_init`, so it finalizes bus initialization when allocation is available. On BCMA, it routes the timer to IRQ7 because hardware/register reporting would otherwise suggest IRQ5. Then `mips_cpu_irq_init()` sets up CPU IRQ lines. If vectored interrupts are supported, each vector directly dispatches its matching IRQ number; otherwise `plat_irq_dispatch()` handles pending bits in priority order.

State and persistence: may update global `cp0_compare_irq` and BCMA core interrupt mask register. CP0 status is modified during dispatch.

Dependencies and integration: depends on BCM47XX bus globals, BCMA APIs under config, MIPS CPU IRQ core, vectored interrupt support, and local bus setup declaration.

Risks: clearing all pending cause/status bits from status before dispatch can affect nested/level interrupt timing. Dispatch uses independent `if` statements, so multiple pending IRQs can be serviced in one entry. BCMA timer routing is hardware-specific and must align with time code.

Test signals: timer interrupts should arrive on IRQ7 for BCMA and scheduling should progress. SSB/BCMA device interrupts should reach their handlers. Boot should log vectored interrupt setup on CPUs with VINT.

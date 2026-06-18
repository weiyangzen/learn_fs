# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-int.c

Purpose: IP22 INT2/INT3 interrupt setup and dispatch. It maps local interrupt status bits to Linux IRQs, handles cascaded mapped interrupts, bus errors, timers, and optional EISA initialization.

Important APIs and control flow: four `irq_chip` instances control local0/local1 and mapped local2/local3 masks. Dispatch helpers read `sgint->istat*`, `vmeistat`, and mask tables to pick the highest-priority IRQ, with a local0 workaround for a FIFO bug. `plat_irq_dispatch()` prioritizes R4k timer, local0, local1, bus error, and 8254 timer. `arch_init_irq()` builds mask-to-IRQ lookup tables, clears masks, initializes CPU IRQs, installs handlers for SGINT IRQ ranges, requests cascade IRQs, and optionally calls `ip22_eisa_init()`.

State, persistence, and integration: state includes lookup arrays and INT mask registers. Dependencies include `sgint` from `sgihpc_init()`, bus-error handler, MIPS CPU IRQ core, and optional EISA. Risks include fragile priority lookup tables, disabled LIO3 path, special non-shareable cascade requests, and hardware errata workaround behavior. Test signals are interrupt routing for serial, SCSI, Ethernet, GIO, panel, timer, and EISA devices.

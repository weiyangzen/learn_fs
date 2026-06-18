<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.c

Purpose: interrupt controller driver for the CPM2 internal SIU interrupt controller.

Important APIs/types/functions: exported-by-header `cpm2_get_irq()` and `cpm2_pic_init()`, IRQ chip callbacks `cpm2_mask_irq()`, `cpm2_unmask_irq()`, `cpm2_ack()`, `cpm2_end_irq()`, `cpm2_set_irq_type()`, mapping tables `irq_to_siureg`/`irq_to_siubit`, and irqdomain ops `cpm2_pic_host_map()`.

Control flow: init masks all interrupts, acknowledges pending bits, reads the vector register, resets priority registers, and creates a linear irqdomain for 64 sources. Mapping installs the CPM2 chip with a level handler by default. `cpm2_get_irq()` reads `ic_sivec`, extracts the vector, and maps it to a Linux IRQ. Type setting validates allowed senses for external and Port C IRQs, selects edge/level handlers, and updates SIEXR edge-detect bits.

State and persistence: global state includes the MMIO pointer, irqdomain, and cached mask words mirrored to SIMRH/SIMRL. Hardware mask, pending, priority, and sense registers persist until changed.

Dependencies and integration points: depends on `cpm2_immr` having been mapped by CPM2 setup, Linux irqdomain/irqchip APIs, device tree interrupt translation, and platform interrupt dispatch calling `cpm2_get_irq()`.

Risks: IRQ numbers do not map linearly to mask bits, so table mistakes break specific sources. External/Port C sense programming is constrained; unsupported high/rising levels are rejected. `cpm2_end_irq()` uses a memory barrier to avoid known spurious IRQ behavior on 82xx systems.

Test signals: boot IRQ discovery, timer/serial/network CPM interrupts, edge-vs-level trigger tests for external and Port C lines, no interrupt storms after EOI, and correct `/proc/interrupts` accounting validate the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.c -->

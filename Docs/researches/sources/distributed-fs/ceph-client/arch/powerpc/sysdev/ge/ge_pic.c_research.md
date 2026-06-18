<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.c

Purpose: Implements a simple cascaded irqdomain driver for GE FPGA board interrupt controllers with 32 level-sensitive inputs.

Important APIs/types/functions: Public interfaces are `gef_pic_init()` and `gef_pic_get_irq()`. Internal elements include `gef_pic_chip`, `gef_pic_host_ops`, `gef_pic_cascade()`, mask/unmask helpers, OF xlate/map callbacks, and global `gef_pic_irq_reg_base`, `gef_pic_irq_host`, and `gef_pic_cascade_irq`.

Control flow: Initialization maps controller registers, masks CPU0/CPU1 interrupt and machine-check outputs, maps the parent cascade IRQ, creates a 32-entry linear irqdomain, and installs a chained handler. The chained handler calls `gef_pic_get_irq()` to find the highest active bit in `INTR_STATUS & CPU0_INTR_MASK`, dispatches the mapped Linux IRQ if present, and EOIs the parent. Child mask/unmask manipulates CPU0 mask bits under a raw spinlock.

State and persistence: Persistent state is the MMIO register base, irqdomain, parent cascade IRQ, and hardware mask registers. There is no per-child software cache; register reads are authoritative.

Dependencies and integration points: Depends on OF address/IRQ parsing, irqdomain, chained IRQ handling, big-endian MMIO, and GE board setup calling `gef_pic_init()`.

Risks: The driver only programs CPU0 mask registers and ignores the dual-output routing described in comments. There is no explicit error handling for failed `of_iomap()` before MMIO writes. Child interrupts have no real acknowledge operation, so devices must deassert their interrupt before unmask or level interrupts can retrigger.

Test signals: GE/SBC610 boot, interrupt delivery for each of 32 inputs, parent cascade EOI behavior, mask/unmask register checks, absent or malformed OF resources, and SMP tests confirming CPU0-only routing is intentional.

Source read size: 254 lines, 6934 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.c

### Purpose
Root interrupt-controller support for MPC8xx SIU PIC.

### Important APIs, Types, And Functions
Defines `mpc8xx_pic_host`, `mpc8xx_cached_irq_mask`, `siu_reg`, irq_chip callbacks `mpc8xx_unmask_irq()`, `mpc8xx_mask_irq()`, `mpc8xx_ack()`, `mpc8xx_end_irq()`, `mpc8xx_set_irq_type()`, public `mpc8xx_get_irq()`, IRQ-domain map/xlate ops, and `mpc8xx_pic_init()`.

### Control Flow
Initialization finds `fsl,pq1-pic` or legacy `mpc8xx-pic`, maps SIU registers, and creates a 64-entry IRQ domain. Runtime IRQ dispatch reads `sc_sivec`, filters the spurious vector, and maps hardware IRQs to Linux IRQs. Per-IRQ chip callbacks manipulate SIU mask, pending, and sense registers.

### State, Persistence, And Dependencies
State includes mapped SIU registers, cached mask bits, and the IRQ domain. No durable persistence. Dependencies include OF address parsing, irq_domain, 8xx IMMR register layout, and Linux IRQ core.

### Integration Points
Machine descriptors use `mpc8xx_pic_init()` and `mpc8xx_get_irq()` as root IRQ plumbing; CPM1 PIC cascades through it.

### Risks
Bit numbering and edge/level sense programming are interrupt-critical. Cached mask state must stay synchronized with hardware.

### Test Signals
Boot 8xx boards, trigger external IRQs, test edge/level configurations, spurious IRQ handling, CPM cascade, and mask/unmask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.c -->

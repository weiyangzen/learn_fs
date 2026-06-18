<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irqtype.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irqtype.h

### Purpose
Defines trigger-type encodings used in Samsung external interrupt configuration registers.

### Important APIs, Types, And Functions
Macros define low level, high level, falling edge, rising edge, and both edge encodings: `S3C2410_EXTINT_LOWLEV`, `S3C2410_EXTINT_HILEV`, `S3C2410_EXTINT_FALLEDGE`, `S3C2410_EXTINT_RISEEDGE`, and `S3C2410_EXTINT_BOTHEDGE`.

### Control Flow
No runtime flow. `s3c_irq_eint_set_type()` translates Linux `IRQ_TYPE_*` flags into these encodings.

### State, Persistence, And Dependencies
No state; encodings are written into EINT control registers.

### Integration Points
Used by S3C64xx external interrupt irqchip code.

### Risks
Wrong encoding produces inverted, missing, or constantly asserted interrupts.

### Test Signals
External interrupt type tests for rising, falling, both-edge, low-level, and high-level modes validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irqtype.h -->

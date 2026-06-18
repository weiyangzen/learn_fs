<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq-s3c64xx.h

### Purpose
Provides S3C64xx interrupt-controller register definitions needed by legacy code.

### Important APIs, Types, And Functions
The header maps IRQ-related register addresses and bit definitions for S3C64xx interrupt handling.

### Control Flow
No direct flow; irqchip setup and EINT handling use register macros from this family.

### State, Persistence, And Dependencies
State is hardware IRQ register state. Depends on mapped S3C64xx MMIO bases.

### Integration Points
Complements `irqs-s3c64xx.h` numeric IRQ definitions and `regs-irqtype.h` trigger encoding definitions.

### Risks
Interrupt mask/pending register mistakes can lose interrupts or cause storms.

### Test Signals
IRQ delivery, masking, acking, and wake events validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq-s3c64xx.h -->

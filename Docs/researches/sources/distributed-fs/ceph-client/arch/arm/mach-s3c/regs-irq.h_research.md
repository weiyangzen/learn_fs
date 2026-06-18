<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq.h

### Purpose
Compatibility wrapper for S3C64xx IRQ register definitions.

### Important APIs, Types, And Functions
No new definitions; includes `regs-irq-s3c64xx.h`.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on S3C64xx IRQ register definitions.

### Integration Points
Used by local code expecting a generic IRQ register include.

### Risks
Hard-selects S3C64xx behavior.

### Test Signals
Compile and IRQ runtime coverage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq.h -->

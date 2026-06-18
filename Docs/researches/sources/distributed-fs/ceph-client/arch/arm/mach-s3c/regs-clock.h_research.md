<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock.h

### Purpose
Compatibility wrapper for S3C64xx clock register definitions.

### Important APIs, Types, And Functions
No new definitions; includes `regs-clock-s3c64xx.h`.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on the S3C64xx register header.

### Integration Points
Used by code that includes generic local clock register names.

### Risks
Hard-selects S3C64xx definitions for all users in this folder.

### Test Signals
Compile and PM/clock runtime coverage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock.h -->

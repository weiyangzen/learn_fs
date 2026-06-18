<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-memport-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-memport-s3c64xx.h

### Purpose
Defines S3C64xx GPIO memory-port drive/control registers used during PM save/restore.

### Important APIs, Types, And Functions
Macros name memory port drive and sleep configuration registers such as `S3C64XX_MEM0DRVCON`, `S3C64XX_MEM1DRVCON`, `S3C64XX_MEM0CONSTOP`, `S3C64XX_MEM1CONSTOP`, and sleep-mode memory control registers.

### Control Flow
No direct flow. `pm-s3c64xx.c` saves and restores these registers around suspend.

### State, Persistence, And Dependencies
State is hardware register content under the S3C64xx GPIO/system register area. Depends on GPIO register base macros.

### Integration Points
Critical for suspend/resume memory bus electrical state and drive strength restoration.

### Risks
Incorrect restore may destabilize external memory or board buses after resume.

### Test Signals
Suspend/resume with memory-intensive stress after wake validates these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-memport-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-sys-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-sys-s3c64xx.h

### Purpose
Defines S3C64xx system controller registers outside the main clock header.

### Important APIs, Types, And Functions
Macros cover system control registers such as `S3C64XX_SPCON` and related system configuration offsets.

### Control Flow
No runtime flow. PM and system setup code access these registers through macros.

### State, Persistence, And Dependencies
State is hardware system-controller content. Depends on mapped system-controller base.

### Integration Points
`pm-s3c64xx.c` saves and restores `S3C64XX_SPCON` during suspend.

### Risks
System configuration bit mistakes can break peripheral routing or resume.

### Test Signals
Peripheral routing after resume and PM register debug output validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-sys-s3c64xx.h -->

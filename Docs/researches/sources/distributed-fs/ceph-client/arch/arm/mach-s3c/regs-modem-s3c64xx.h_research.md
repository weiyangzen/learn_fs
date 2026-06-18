<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-modem-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-modem-s3c64xx.h

### Purpose
Defines S3C64xx modem interface register addresses used by system suspend save/restore.

### Important APIs, Types, And Functions
Key macros include modem MIFP control register definitions such as `S3C64XX_MODEM_MIFPCON`.

### Control Flow
No direct flow; PM code saves and restores the modem interface register.

### State, Persistence, And Dependencies
State is in S3C64xx modem MMIO registers. Depends on `S3C64XX_VA_MODEM`.

### Integration Points
`pm-s3c64xx.c` includes this header for `misc_save[]`.

### Risks
Incorrect modem bus state can affect attached modem or shared bus hardware across suspend.

### Test Signals
Suspend/resume on boards using modem/host interface functions validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-modem-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-syscon-power-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-syscon-power-s3c64xx.h

### Purpose
Defines S3C64xx power-control system-controller registers and bit fields used by suspend and power domains.

### Important APIs, Types, And Functions
Macros describe `S3C64XX_NORMAL_CFG`, `S3C64XX_PWR_CFG`, `S3C64XX_WAKEUP_STAT`, `S3C64XX_BLK_PWR_STAT`, domain enable bits, WFI sleep mode encoding, wake disable bits for RTC/touch/SD/MMC/modem/HSI, and `INFORM0`.

### Control Flow
No direct flow. PM domain code toggles domain bits; suspend preparation writes wake masks, resume address, and WFI mode.

### State, Persistence, And Dependencies
State is in always-on system controller registers. Depends on the S3C64xx system virtual base.

### Integration Points
Core to `pm-s3c64xx.c` and wake-mask synchronization.

### Risks
Power bits are destructive if wrong: they can gate active domains, block wake sources, or make WFI enter the wrong low-power mode.

### Test Signals
Domain power-cycle tests, suspend entry, wake-stat reads, and wake-source matrix testing validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-syscon-power-s3c64xx.h -->

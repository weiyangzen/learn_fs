<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock-s3c64xx.h

### Purpose
Defines S3C64xx clock and power-management register addresses and bit fields.

### Important APIs, Types, And Functions
The header maps registers through `S3C_VA_SYS`, including AHB/APB clock gates, `S3C64XX_NORMAL_CFG`, `S3C64XX_BLK_PWR_STAT`, `S3C64XX_PWR_CFG`, `S3C64XX_WAKEUP_STAT`, `S3C64XX_INFORM0`, and related PLL/clock control definitions.

### Control Flow
No runtime flow. PM, clock, and reset code use these macros with raw MMIO accessors.

### State, Persistence, And Dependencies
State is hardware register content. The header depends on S3C64xx system controller virtual mapping.

### Integration Points
Used by S3C64xx common init, PM domain control, suspend preparation, and wake status handling.

### Risks
Wrong bit definitions can power off active domains or prevent resume. Register access assumes `S3C_VA_SYS` was mapped.

### Test Signals
Clock initialization, PM domain toggling, suspend/resume, and wake-stat logging validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock-s3c64xx.h -->

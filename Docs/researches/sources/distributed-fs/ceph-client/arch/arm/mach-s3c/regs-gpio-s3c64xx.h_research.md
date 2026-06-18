<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-s3c64xx.h

### Purpose
Defines S3C64xx GPIO bank base addresses, per-bank register offsets, external interrupt registers, and GPIO helper address macros.

### Important APIs, Types, And Functions
Macros include `S3C64XX_GPIOREG()`, bank bases `S3C64XX_GPA_BASE` through `S3C64XX_GPQ_BASE`, bank register accessors for `CON`, `DAT`, `PUD`, and drive control, plus EINT0 control/mask/pending registers.

### Control Flow
No runtime flow; GPIO, IRQ, setup, and PM code use these constants for MMIO.

### State, Persistence, And Dependencies
State is in hardware GPIO/EINT registers. The header depends on `S3C64XX_VA_GPIO` mapping and Samsung GPIO encoding.

### Integration Points
Used by external interrupt setup in `s3c64xx.c`, GPIO PM restore, setup helpers for I2C/SDHCI/keypad/framebuffer/SPI, and board GPIO calls.

### Risks
Register layout differs by bank; wrong offsets or pull definitions can misconfigure pins, break wakeup, or short board signals.

### Test Signals
GPIO direction/value/pull tests, external interrupt type tests, and peripheral pinmux validation are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-s3c64xx.h -->

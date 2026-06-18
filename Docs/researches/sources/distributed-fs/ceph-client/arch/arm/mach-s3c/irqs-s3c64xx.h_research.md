<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs-s3c64xx.h

### Purpose
Defines the legacy S3C64xx interrupt number layout used by non-DT ARM machine code. It assigns VIC0/VIC1 lines, linear external interrupt numbers, grouped GPIO interrupt ranges, board IRQ start, and compatibility aliases.

### Important APIs, Types, And Functions
The key macros are `S3C_IRQ()`, `S3C64XX_IRQ_VIC0()`, `S3C64XX_IRQ_VIC1()`, `S3C_EINT()`, `IRQ_EINT()`, `IRQ_EINT_GROUP()`, `IRQ_BOARD_START`, and `S3C64XX_NR_IRQS`. Named IRQ constants cover timers, UARTs, DMA, SDHCI, RTC, ADC/touch, USB, SPI, I2C, display, and media engines.

### Control Flow
There is no runtime flow. The numeric layout is consumed at compile time by irqchip setup, board files, platform device resources, wake mask code, and drivers that still use platform IRQ numbers.

### State, Persistence, And Dependencies
No mutable state is stored here. The persistent contract is the stable IRQ numbering ABI inside this kernel tree. It depends on the ARM legacy IRQ model and the S3C64xx two-VIC hardware topology.

### Integration Points
`s3c64xx.c`, `s3c6410.c`, platform resources, board files such as Cragganmore, and power-management wake masking all rely on these definitions.

### Risks
Shared aliases such as `IRQ_HSMMC2` mapped to `IRQ_SPI1` and SoC-specific overlaps need careful driver use. Changing offsets or group sizes would break platform data and wake handling.

### Test Signals
Boot tests should confirm VIC registration, external interrupt demuxing, SDHCI/SPI shared IRQ behavior, and board-specific GPIO interrupt use. Build tests catch missing aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs-s3c64xx.h -->

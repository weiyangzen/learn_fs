# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung-s3c64xx.h

Purpose: S3C64xx GPIO bank numbering and address macros.

Important APIs/types/functions: defines bank sizes, global GPIO numbers such as `S3C64XX_GPA(n)` through later banks, base addresses, and `S3C_GPIO_END`.

Control flow: no executable flow.

State and persistence: constants define the legacy global GPIO namespace and bank layout.

Dependencies and integration points: used by `gpio-samsung.c`, board headers, and peripheral setup files.

Risks: global numbering must remain consistent with registered gpio_chip bases. Off-by-one bank sizes cause lookup and IRQ mapping errors.

Test signals: gpiochip ranges in debugfs/sysfs, board GPIO constants, and IRQ mapping for GPN/GPL/GPM banks.

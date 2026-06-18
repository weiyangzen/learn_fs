# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-uart.c

Purpose: common helper layer for registering Samsung legacy UART platform devices.

Important APIs/types/functions: functions include `s3c24xx_init_uartdevs()` and related setup that copies board `s3c2410_uartcfg` into serial platform data.

Control flow: CPU/board init passes UART resources and configs; this file creates/initializes platform device data for each configured port.

State and persistence: stores static platform data/resources for UART devices during boot.

Dependencies and integration points: used by `cpu.h` declarations, S3C64xx UART resources, and the Samsung serial driver.

Risks: shallow copying or wrong count can register ports with stale config. Legacy path is tied to ATAGS.

Test signals: serial platform devices present, console works on configured port, and UART count/config match board data.

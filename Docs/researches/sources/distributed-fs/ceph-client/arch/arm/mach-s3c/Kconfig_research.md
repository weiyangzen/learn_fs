# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/Kconfig

Purpose: common Samsung S3C/S3C64xx platform configuration, especially legacy ATAGS support.

Important APIs/types/functions: sources S3C64xx Kconfig, defines `PLAT_SAMSUNG`, `SAMSUNG_PM`, `S3C_LOWLEVEL_UART_PORT`, `SAMSUNG_ATAGS`, legacy device options (`S3C_DEV_*`, `SAMSUNG_DEV_*`), `GPIO_SAMSUNG`, `SAMSUNG_PM_GPIO`, and `SAMSUNG_WAKEMASK`.

Control flow: build-time only. DT-only platforms avoid ATAGS static devices, while legacy platforms select GPIO, device definitions, PM GPIO save/restore, and wake-mask helpers.

State and persistence: no local runtime state; selected options control which static platform devices and PM helpers are linked.

Dependencies and integration points: coordinates Makefile objects for `init`, `cpu`, `devs`, UART, GPIO, PM, and wake mask.

Risks: legacy ATAGS split means code may silently not build for DT platforms. Deprecated platform notice in CPU init underscores removal risk.

Test signals: config builds for DT-only and SAMSUNG_ATAGS paths, GPIO/PM option combinations, and low-level UART selection.

# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/Makefile

Purpose: build object selection for Samsung S3C platform support.

Important APIs/types/functions: includes `Makefile.s3c64xx`, always builds `init.o cpu.o`, builds platform data/devices/UART under `CONFIG_SAMSUNG_ATAGS`, builds `gpio-samsung.o` under `CONFIG_GPIO_SAMSUNG`, and PM helpers under `CONFIG_SAMSUNG_PM`, `CONFIG_SAMSUNG_PM_GPIO`, and `CONFIG_SAMSUNG_WAKEMASK`.

Control flow: make-time object inclusion only.

State and persistence: none.

Dependencies and integration points: mirrors Kconfig split between common CPU init, legacy static devices, GPIO, and PM.

Risks: missing object selection produces link failures or missing runtime platform support for legacy boards.

Test signals: build matrix across ATAGS, GPIO, PM, and wake-mask settings.

## sources/distributed-fs/ceph-client/arch/mips/ath25/prom.c

Purpose: provides the ATH25 PROM initialization hook. In this source version `prom_init()` is intentionally empty.

Important APIs and functions: `prom_init()` is marked `__init` and satisfies the MIPS platform firmware initialization interface.

Control flow: no operations are performed. ATH25 setup is handled by later platform hooks in `board.c` and family-specific files rather than parsing firmware data here.

State and persistence: none.

Dependencies and integration: includes `linux/init.h` and `asm/bootinfo.h`. The file is always linked by the ATH25 Makefile.

Risks: any bootloader argument, environment, or memory information not handled elsewhere will be ignored. This is acceptable only because ATH25 code determines memory and board configuration from hardware/flash.

Test signals: boot should proceed to `plat_mem_setup()` without requiring PROM data. There are no direct log messages.

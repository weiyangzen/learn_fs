## sources/distributed-fs/ceph-client/arch/mips/ath79/prom.c

Purpose: initializes ATH79 firmware-provided command-line data and optional initrd placement.

Important APIs and functions: `prom_init()` calls `fw_init_cmdline()`. When `CONFIG_BLK_DEV_INITRD` is enabled, it reads `initrd_start` and `initrd_size` from firmware environment variables using `fw_getenvl()`, converts the start address through `KSEG0ADDR()`, and fills `initrd_start`/`initrd_end`.

Control flow: command-line initialization always runs. Initrd setup runs only when configured and only if `initrd_start` is nonzero.

State and persistence: updates global boot command line and initrd address variables for this boot only. No persistent storage is changed.

Dependencies and integration: depends on MIPS firmware helper APIs, bootinfo, initrd globals, and `common.h`. `setup.c` later reads firmware `fdt_start` separately.

Risks: firmware environment values are trusted. A wrong physical initrd address or size can point into invalid memory. If `initrd_start` is absent, no initrd is registered.

Test signals: kernel command line should reflect firmware arguments. Initrd-enabled boots should find the initrd at the expected converted address and mount/unpack it successfully.

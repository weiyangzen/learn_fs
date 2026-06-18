<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/env.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/env.c

Purpose: Parses Loongson64 firmware environment, selects/fixes a DTB, initializes system configuration, and records firmware table pointers.

Important APIs/types/functions: Exports `cpu_clock_freq`, `loongson_memmap`, `loongson_sysconf`, firmware table pointers, chip control address arrays, and `smp_group[]`. `prom_dtb_init_env()` handles DTB boot, `prom_lefi_init_env()` handles LEFI boot, and `lefi_fixup_fdt()` patches UART clock-frequency properties.

Control flow: DTB mode accepts `fw_arg2` as FDT when plausible or falls back to built-in 2K1000 DTB. LEFI mode walks boot parameter offsets, fills CPU/node counts, DMA coherency, reset/suspend/VBIOS addresses, bridge type, workarounds, SMP mailbox bases, chipcfg/temp/frequency-control bases, and chooses a built-in DTB by PRID and bridge. UART entries from firmware update the chosen FDT.

State and persistence: Populates global platform configuration used by memory, DMA, SMP, reset, PM, time, sysfs, and PCI quirks. The fixed-up FDT buffer is static initdata.

Dependencies and integration: Uses LEFI boot structures, libfdt, built-in DTB symbols, PCI vendor IDs, Loongson PRID constants, and bridge early-config callbacks.

Risks: Firmware offsets and strings are trusted. The 16 KiB FDT fixup buffer can be too small. Unknown bridge defaults to virtual DTB and may not describe real hardware.

Test signals: Boot logs should report DMA coherency, CPU clock, and bridge type; `/proc/device-tree` UART clocks should match firmware; SMP group and reset addresses should match board firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/env.c -->

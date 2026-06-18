# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo-pvr-full.c

Purpose: overlays full Processor Version Register data onto the architecture `struct cpuinfo`, using DTS/static data as the initial baseline and warning when hardware and device-tree expectations differ.

Important APIs and state: `set_cpuinfo_pvr_full(struct cpuinfo *ci, struct device_node *cpu)` reads all PVR registers via `get_pvr()`. The `CI()` macro copies individual PVR fields into `ci`; `err_printk()` records mismatches for instruction, multiplier/FPU, and write-back cache policy groups.

Control flow: the function first checks `PVR_VERSION`; a zero version is treated as broken PVR and leaves DTS data in place. It then fills instruction, multiply, FPU, exception, cache, bus, FSL, interrupt polarity, debug-breakpoint, user, MMU, endian, and FPGA family fields. Cache line length is converted from PVR words to bytes with `<< 2`.

State and persistence: it mutates only the boot-time global `cpuinfo` instance supplied by caller. That state persists for cache setup, `/proc/cpuinfo`, timers, MMU setup, and debug code.

Dependencies and integration: depends on `asm/pvr.h` extractor macros and `pvr.c`. Called from `setup_cpuinfo()` only when PVR support indicates full CPU PVR use.

Risks and test signals: the mismatch warnings are diagnostic only, so bad DTS can still boot with hardware-derived fields. A broken or partial PVR can poison cache parameters. Test by booting systems with known PVR values, checking `/proc/cpuinfo`, cache line sizes, and mismatch logs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_csa.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_csa.h

Purpose: Defines the SPU context save area layout and register save/restore status codes.

Important APIs/types/functions: SPU GPR/SPR counts, save/restore magic values, stopped-status constants, and `struct spu_lscsa`-style local-store save layout definitions. Source-visible declarations include: #define _SPU_CSA_H_; #define NR_SPU_GPRS 128; #define NR_SPU_SPRS 9; #define NR_SPU_REGS_PAD 7; #define NR_SPU_SPILL_REGS 144 /* GPRS + SPRS + PAD */; #define SIZEOF_SPU_SPILL_REGS NR_SPU_SPILL_REGS * 16; #define SPU_SAVE_COMPLETE 0x3FFB; #define SPU_RESTORE_COMPLETE 0x3FFC.

Control flow: SPU context switch code uses these layouts to save local store and architectural state between contexts. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: context save areas persist per SPU context and may be consumed by coredumps or restore code. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with spufs context switching, Cell low-level save/restore assembly, and coredump support.

Risks: layout and alignment must match SPU microcode/assembly expectations or context restore corrupts user state. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 247 lines, 6167 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_csa.h -->

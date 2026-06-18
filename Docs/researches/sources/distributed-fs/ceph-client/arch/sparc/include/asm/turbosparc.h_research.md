# sources/distributed-fs/ceph-client/arch/sparc/include/asm/turbosparc.h

Purpose: SPARC architecture header `turbosparc.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `turbosparc_inv_insn_tag`, `turbosparc_inv_data_tag`, `turbosparc_flush_icache`, `turbosparc_flush_dcache`, `turbosparc_idflash_clear`, `turbosparc_set_ccreg`, `turbosparc_get_ccreg`; macros/constants `_SPARC_TURBOSPARC_H`, `TURBOSPARC_MMUENABLE`, `TURBOSPARC_NOFAULT`, `TURBOSPARC_ICSNOOP`, `TURBOSPARC_PSO`, `TURBOSPARC_DCENABLE`, `TURBOSPARC_ICENABLE`, `TURBOSPARC_BMODE`, `TURBOSPARC_PARITYODD`, `TURBOSPARC_PCENABLE`, `TURBOSPARC_SCENABLE`, `TURBOSPARC_uS2`, `TURBOSPARC_WTENABLE`, `TURBOSPARC_SNENABLE`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TURBOSPARC_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is inline assembly.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`, `asm/pgtsrmmu.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.

# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tsunami.h

Purpose: SPARC architecture header `tsunami.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `tsunami_flush_icache`, `tsunami_flush_dcache`; macros/constants `_SPARC_TSUNAMI_H`, `TSUNAMI_SW`, `TSUNAMI_AV`, `TSUNAMI_DV`, `TSUNAMI_MV`, `TSUNAMI_PC`, `TSUNAMI_ITD`, `TSUNAMI_ALC`, `TSUNAMI_PE`, `TSUNAMI_RCMASK`, `TSUNAMI_IENAB`, `TSUNAMI_DENAB`, `TSUNAMI_NF`, `TSUNAMI_ME`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TSUNAMI_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is inline assembly.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.

# sources/distributed-fs/ceph-client/arch/sparc/include/asm/swift.h

Purpose: SPARC architecture header `swift.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `swift_inv_insn_tag`, `swift_inv_data_tag`, `swift_flush_dcache`, `swift_flush_icache`, `swift_idflash_clear`, `swift_flush_page`, `swift_flush_segment`, `swift_flush_region`, `swift_flush_context`; macros/constants `_SPARC_SWIFT_H`, `SWIFT_ST`, `SWIFT_WP`, `SWIFT_BF`, `SWIFT_PMC`, `SWIFT_PE`, `SWIFT_PC`, `SWIFT_AP`, `SWIFT_AC`, `SWIFT_BM`, `SWIFT_RC`, `SWIFT_IE`, `SWIFT_DE`, `SWIFT_SA`, `SWIFT_NF`, `SWIFT_EN`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_SWIFT_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is inline assembly.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.

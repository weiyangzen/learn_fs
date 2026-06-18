# sources/distributed-fs/ceph-client/arch/sparc/include/asm/signal.h

Purpose: SPARC architecture header `signal.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: macros/constants `__SPARC_SIGNAL_H`, `__ARCH_HAS_KA_RESTORER`, `__ARCH_HAS_SA_RESTORER`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SIGNAL_H`, `__ASSEMBLER__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `linux/personality.h`, `linux/types.h`, `uapi/asm/signal.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are ABI compatibility breaks. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.

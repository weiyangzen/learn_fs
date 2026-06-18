# sources/distributed-fs/ceph-client/arch/sparc/include/asm/seccomp.h

Purpose: SPARC architecture header `seccomp.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: macros/constants `_ASM_SECCOMP_H`, `__NR_seccomp_sigreturn_32`.

Control flow: The file is driven by preprocessor gates such as `_ASM_SECCOMP_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `linux/unistd.h`, `asm-generic/seccomp.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.

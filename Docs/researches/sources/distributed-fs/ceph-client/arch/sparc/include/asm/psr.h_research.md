# sources/distributed-fs/ceph-client/arch/sparc/include/asm/psr.h

Purpose: Kernel wrapper around SPARC PSR definitions with inline helpers to read/write `%psr` and read the floating-point status register.

Important APIs/types/functions: functions/helpers `get_psr`, `put_psr`, `get_fsr`; macros/constants `__LINUX_SPARC_PSR_H`.

Control flow: The file is driven by preprocessor gates such as `__LINUX_SPARC_PSR_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is architectural: PSR condition/supervisor/PIL/window bits and FSR contents; `put_psr` writes directly to CPU control state.

Dependencies and integration points: Includes/dependencies: `uapi/asm/psr.h`. Integration points include scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, ABI compatibility breaks. Test signals: Trap entry/return, interrupt enable/disable, context switching, and FPU exception handling are test signals.

# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine_32.h

Purpose: SPARC32 soft-float machine description for Linux math emulation, defining word sizes, multiply/divide meat macros, NaN selection, rounding, exception bits, and fraction helpers.

Important APIs/types/functions: macros/constants `_SFP_MACHINE_H`, `_FP_W_TYPE_SIZE`, `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_I_TYPE`, `_FP_MUL_MEAT_S`, `_FP_MUL_MEAT_D`, `_FP_MUL_MEAT_Q`, `_FP_DIV_MEAT_S`, `_FP_DIV_MEAT_D`, `_FP_DIV_MEAT_Q`, `_FP_NANFRAC_S`, `_FP_NANFRAC_D`, `_FP_NANFRAC_Q`, `_FP_NANSIGN_S`, `_FP_NANSIGN_D`, `_FP_NANSIGN_Q`, `_FP_KEEPNANFRACP`, plus 17 more.

Control flow: The file is driven by preprocessor gates such as `_SFP_MACHINE_H`, `CONFIG_SMP`, `FP_ROUNDMODE`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP paths rather than through standalone functions.

State and persistence behavior: State is per-operation macro local state plus caller-provided exception accumulators; no kernel global state is introduced.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management, SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, configuration-specific build gaps. Test signals: Soft-float single/double/quad arithmetic, NaN propagation, rounding modes, and trap exception flag compatibility are test signals.

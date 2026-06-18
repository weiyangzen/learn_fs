# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine_64.h

Purpose: SPARC64 soft-float machine description optimized for 64-bit words, defining arithmetic meat macros, NaN payloads, rounding-mode access, exception bits, and quad helpers.

Important APIs/types/functions: macros/constants `_SFP_MACHINE_H`, `_FP_W_TYPE_SIZE`, `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_I_TYPE`, `_FP_MUL_MEAT_S`, `_FP_MUL_MEAT_D`, `_FP_MUL_MEAT_Q`, `_FP_DIV_MEAT_S`, `_FP_DIV_MEAT_D`, `_FP_DIV_MEAT_Q`, `_FP_NANFRAC_S`, `_FP_NANFRAC_D`, `_FP_NANFRAC_Q`, `_FP_NANSIGN_S`, `_FP_NANSIGN_D`, `_FP_NANSIGN_Q`, `_FP_KEEPNANFRACP`, plus 10 more.

Control flow: The file is driven by preprocessor gates such as `_SFP_MACHINE_H`, `FP_ROUNDMODE`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State is carried through soft-fp macro variables and FSR-derived rounding/exception values supplied by the math-emulation caller.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift. Test signals: 64-bit math emulation, quad precision operations, NaN/sign handling, and exception flag reporting should be tested.

# sources/distributed-fs/ceph-client/arch/sparc/include/asm/scratchpad.h

Purpose: Constant/ABI header for `scratchpad.h` supplying numeric definitions consumed by low-level SPARC code.

Important APIs/types/functions: macros/constants `_SPARC64_SCRATCHPAD_H`, `SCRATCHPAD_MMU_MISS`, `SCRATCHPAD_CPUID`, `SCRATCHPAD_UTSBREG1`, `SCRATCHPAD_UTSBREG2`, `SCRATCHPAD_UNUSED1`, `SCRATCHPAD_UNUSED2`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SCRATCHPAD_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State is external hardware or ABI state represented by constants; the header itself has no mutable storage.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: Compile-time users plus boot/runtime paths that decode these constants are the main tests.

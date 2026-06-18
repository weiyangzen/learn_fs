# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sigcontext.h

Purpose: Kernel-visible SPARC signal-context layouts for 32-bit and 64-bit signal frames, including saved register windows, FPU state pointers, masks, and stack metadata.

Important APIs/types/functions: types `sigcontext32`, `sigcontext`; macros/constants `__SPARC_SIGCONTEXT_H`, `__SUNOS_MAXWIN`, `__SIGC_MAXWIN`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SIGCONTEXT_H`, `__ASSEMBLER__`, `CONFIG_SPARC64`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: This defines ABI-persistent user-frame state; changing field order or sizes breaks signal restore and compatibility.

Dependencies and integration points: Includes/dependencies: `asm/ptrace.h`, `uapi/asm/sigcontext.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps, ABI compatibility breaks. Test signals: Signal delivery/return, compat signal frames, alternate stacks, saved windows, and FPU state restore are the test signals.

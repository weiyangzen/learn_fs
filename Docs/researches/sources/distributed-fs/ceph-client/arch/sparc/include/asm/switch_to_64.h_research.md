# sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to_64.h

Purpose: sparc64 context-switch contract that flushes VIS state, calls `__switch_to`, and exposes user-window synchronization/fault-in helpers.

Important APIs/types/functions: types `pt_regs`; functions/helpers `synchronize_user_stack`, `fault_in_user_windows`; macros/constants `__SPARC64_SWITCH_TO_64_H`, `prepare_arch_switch`, `switch_to`.

Control flow: The file is driven by preprocessor gates such as `__SPARC64_SWITCH_TO_64_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State is in `thread_info`, FPRS/VIS/FPU state, register windows, and the returned previous task pointer.

Dependencies and integration points: Includes/dependencies: `asm/visasm.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes. Test signals: VIS/FPU context switching, ptrace/signal window synchronization, and scheduler switch correctness should be covered.

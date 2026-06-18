# sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor_64.h

Purpose: sparc64 task processor-state definition: 32/64-bit task size selection, stack tops, thread debug-lock data, `start_thread`/`start_thread32`, prefetch helpers, and math emulation hooks.

Important APIs/types/functions: types `thread_struct`, `task_struct`; functions/helpers `__get_wchan`, `prefetch`, `prefetchw`, `do_mathemu`; macros/constants `__ASM_SPARC64_PROCESSOR_H`, `VA_BITS`, `VPTE_SIZE`, `TASK_SIZE_OF`, `TASK_SIZE`, `STACK_TOP32`, `STACK_TOP64`, `STACK_TOP`, `STACK_TOP_MAX`, `INIT_THREAD`, `TSTATE_INITIAL_MM`, `start_thread`, `start_thread32`, `task_pt_regs`, `KSTK_EIP`, `KSTK_ESP`, `ARCH_HAS_PREFETCH`, `ARCH_HAS_PREFETCHW`, plus 1 more.

Control flow: The file is driven by preprocessor gates such as `__ASM_SPARC64_PROCESSOR_H`, `__ASSEMBLER__`, `__KERNEL__`, `CONFIG_DEBUG_SPINLOCK`, `CONFIG_SMP`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, locking, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is stored in `pt_regs`, thread-info window/FPU fields, utrap reference counts, FPRS/XFSR bits, and task flags such as `TIF_32BIT`.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`, `asm/pstate.h`, `asm/ptrace.h`, `asm/page.h`, `linux/types.h`, `asm/fpumacro.h`. Integration points include memory-management, SMP, locking, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: 64-bit and compat exec, utrap cleanup, FPU reset, user stack setup, mmap layout, and prefetch-enabled builds should be tested.

# sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor_32.h

Purpose: SPARC32 task processor-state definition: user address bounds, thread FP/window state, `start_thread()`, kernel stack register access, math emulation hooks, and idle callback declaration.

Important APIs/types/functions: types `task_struct`, `fpq`, `thread_struct`; functions/helpers `start_thread`, `__get_wchan`, `do_mathemu`, `void`; macros/constants `__ASM_SPARC_PROCESSOR_H`, `TASK_SIZE`, `STACK_TOP`, `STACK_TOP_MAX`, `INIT_THREAD`, `task_pt_regs`, `KSTK_EIP`, `KSTK_ESP`.

Control flow: The file is driven by preprocessor gates such as `__ASM_SPARC_PROCESSOR_H`, `__KERNEL__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into scheduler/task paths rather than through standalone functions.

State and persistence behavior: State persists in `thread_struct`, saved register windows, FPU queue/status, `last_task_used_math`, and the initial user pt_regs window created by `start_thread`.

Dependencies and integration points: Includes/dependencies: `asm/psr.h`, `asm/ptrace.h`, `asm/head.h`, `asm/signal.h`, `asm/page.h`. Integration points include scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: Exec, fork, signal delivery, FP emulation, window spill/fill, and kernel stack unwinding are the test signals.

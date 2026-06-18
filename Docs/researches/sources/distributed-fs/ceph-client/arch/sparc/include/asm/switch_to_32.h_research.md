# sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to_32.h

Purpose: SPARC32 context-switch macro contract, saving lazy FPU state when `TIF_USEDFPU` is set and calling low-level `__switch_to`.

Important APIs/types/functions: functions/helpers `fpsave`, `synchronize_user_stack`; macros/constants `__SPARC_SWITCH_TO_H`, `SWITCH_ENTER`, `SWITCH_DO_LAZY_FPU`, `prepare_arch_switch`, `switch_to`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SWITCH_TO_H`, `CONFIG_SMP`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State moves among `thread_struct` fields, `%psr`, register windows, saved FPU registers, and per-task kernel stack pointers.

Dependencies and integration points: Includes/dependencies: `asm/smp.h`. Integration points include memory-management, SMP, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, configuration-specific build gaps. Test signals: Scheduler stress, lazy FPU handoff, user-window synchronization, fork/exec switch paths, and SMP switching are signals.

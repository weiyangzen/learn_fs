# sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info_32.h

Purpose: SPARC32 `thread_info` layout used by trap, scheduler, syscall, and window spill code, including register-window buffers, flags, counters, CPU id, and kernel saved state offsets.

Important APIs/types/functions: types `thread_info`; functions/helpers `asm`; macros/constants `_ASM_THREAD_INFO_H`, `NSWINS`, `INIT_THREAD_INFO`, `current_thread_info`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `TI_UWINMASK`, `TI_TASK`, `TI_FLAGS`, `TI_CPU`, `TI_PREEMPT`, `TI_SOFTIRQ`, `TI_HARDIRQ`, `TI_KSP`, `TI_KPC`, `TI_KPSR`, `TI_KWIM`, `TI_REG_WINDOW`, plus 20 more.

Control flow: The file is driven by preprocessor gates such as `_ASM_THREAD_INFO_H`, `__KERNEL__`, `__ASSEMBLER__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP, syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: This is persistent per-task low-level state at the base of the kernel stack; assembly depends on every `TI_*` offset and flag bit.

Dependencies and integration points: Includes/dependencies: `asm/ptrace.h`, `asm/page.h`. Integration points include SMP, syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, MMU/TLB encoding regressions. Test signals: Context switch, preemption counters, signal/window save, syscall work masks, and assembly-offset validation are test signals.

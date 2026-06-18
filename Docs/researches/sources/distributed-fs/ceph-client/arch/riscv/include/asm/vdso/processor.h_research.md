<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/processor.h

Purpose: Defines RISC-V task CPU state, process memory-layout constants, prefetch hooks, vector context flags, and thread startup interfaces.

Important APIs/types/functions: Key items are `struct thread_struct`, `INIT_THREAD`, `task_pt_regs()`, `KSTK_EIP`, `KSTK_ESP`, `TASK_UNMAPPED_BASE`, `STACK_TOP`, `user_max_virt_addr()`, prefetch helpers, `start_thread()`, `__get_wchan()`, and `wait_for_interrupt()`.

Control flow: Most logic is macro/inline: stack and mmap bounds derive from VA bits and compat state, `task_pt_regs()` locates saved registers at the top of the kernel stack, and optional prefetch emits Zicbop alternatives.

State and persistence: Per-task persistent state stores callee-saved GPRs, FPU/vector state, envcfg, SUM, bad cause, alignment control, and SMP icache-migration flags.

Dependencies and integration points: Used by scheduler, exec, ptrace, traps, vector/FPU context code, mmap, and arch thread lifecycle.

Risks: Struct layout feeds assembly offsets; wrong vector flags or stack calculations corrupt context switches or signal/ptrace state.

Test signals: Context-switch stress, exec/signal/ptrace tests, vector/FPU save-restore, mmap layout tests, SMP migration icache tests, and asm-offset rebuilds.

Source read size: 29 lines, 592 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/processor.h

Purpose: defines LoongArch task CPU state, architecture thread layout, task-size limits, CPU idle hooks, and process/thread helpers.
Important APIs and types: provides `struct thread_struct` with saved callee registers, CSR/FPU/LBT state, hardware breakpoint arrays, and address-limit state; declares `cpu_probe`, `start_thread`, `release_thread`, `arch_dup_task_struct`, `copy_thread`, `get_wchan`, `__KSTK_TOS`, and idle helpers.
Control flow: generic scheduler and fork code use this header to create, copy, and restore task CPU context. Debug, ptrace, FPU, and hardware breakpoint code read and update fields in `thread_struct`.
State and persistence: the structure persists per-task register state across context switches, lazy FPU/vector state, user TLS, and per-task debug resources. Constants such as `TASK_SIZE`, `STACK_TOP`, and `STACK_TOP_MAX` define user address-space bounds.
Dependencies and integration: integrates with `asm/ptrace.h`, `asm/fpu.h`, `asm/page.h`, `asm/hw_breakpoint.h`, generic scheduler, ELF core dump code, and syscall entry/return paths.
Risks and test signals: layout changes must stay synchronized with assembly offsets and switch code. Signals include fork/exec, ptrace, coredump, lazy FPU/vector, hardware breakpoint, and stack unwinding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/processor.h -->

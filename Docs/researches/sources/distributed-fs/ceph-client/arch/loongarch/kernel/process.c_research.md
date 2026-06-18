## sources/distributed-fs/ceph-client/arch/loongarch/kernel/process.c

### Purpose
`process.c` implements LoongArch process/thread lifecycle support: user-mode thread setup, fork context copying, kernel-thread return paths, FPU/SIMD/LBT state handling across duplication, wait-channel lookup, stack classification, userspace stack randomization, cross-CPU backtraces, and ELF core register dumps.

### Important APIs, Types, And Functions
Important functions include `start_thread`, `flush_thread`, `arch_dup_task_struct`, `ret_from_fork`, `ret_from_kernel_thread`, `copy_thread`, `__get_wchan`, `get_stack_info`, `stack_top`, `arch_align_stack`, `arch_trigger_cpumask_backtrace`, and `loongarch_dump_regs32/64`. Global exports include stack canary support and `boot_option_idle_override`.

### Control Flow
`start_thread` drops privilege to PLV user, disables FP in EUEN, clears live math/SIMD/LBT flags, sets PC and SP, and resets FCSR. `arch_dup_task_struct` saves any live hardware FPU/SIMD state before copying task data, then copies only the relevant thread-state prefix plus optional LBT state unless RANDSTRUCT forces a full copy. `copy_thread` builds child `pt_regs` at the top of the kernel stack, sets scheduler return addresses for user or kernel threads, handles TLS, and clears lazy hardware ownership flags.

### State, Persistence, And Dependencies
Persistent per-task state is `thread_struct`, saved registers, FPU/SIMD/LBT context, hw breakpoints, VDSO placement, and task stack metadata. The code depends on LoongArch ABI register conventions, lazy FPU helpers, ptrace hardware breakpoint copying, unwinder APIs, stack layout constants, randomization, and NMI/backtrace infrastructure.

### Integration Points
Scheduler context switch assembly consumes fields set here. Exec and fork paths call these hooks. Signal, ptrace, perf, stacktrace, and core-dump code depend on consistent `pt_regs` and thread-state layout. Backtrace IPIs integrate with SMP call-single infrastructure.

### Risks
Lazy FPU/SIMD/LBT duplication is race-prone; saving live hardware state under preemption disable is essential. `copy_thread` must set child return registers exactly or fork/kernel-thread startup will return to the wrong path. Stack-info helpers trust saved stack sentinels for IRQ stacks and can misclassify corrupted stacks. VDSO stack-top reservation affects userspace ABI layout.

### Test Signals
Run fork/clone/exec, kernel thread creation, TLS tests, FP/LSX/LASX/LBT workloads across fork, ptrace hardware breakpoint inheritance, `/proc/<pid>/wchan`, stacktrace reliability, core dumps, and sysrq/NMI CPU backtraces.

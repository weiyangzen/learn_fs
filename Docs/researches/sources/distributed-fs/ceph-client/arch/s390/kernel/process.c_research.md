# sources/distributed-fs/ceph-client/arch/s390/kernel/process.c

Purpose: implements s390 process and thread mechanics: fork return, task duplication, thread creation, context switching, exec cleanup, wait-channel lookup, and userspace address randomization.

Important APIs/functions: architecture entry points include `__ret_from_fork()`, `flush_thread()`, `arch_setup_new_exec()`, `arch_release_task_struct()`, `arch_dup_task_struct()`, `copy_thread()`, `execve_tail()`, `__switch_to()`, `__get_wchan()`, `arch_align_stack()`, and `arch_randomize_brk()`.

Control flow: forked tasks enter `ret_from_fork`, call `schedule_tail()`, execute the kernel-thread function if the saved regs are not user mode, then go through `syscall_exit_to_user_mode()`. `arch_dup_task_struct()` snapshots FPU state and copies the task, but clears runtime instrumentation and guarded-storage pointers to avoid double ownership. `copy_thread()` builds the fake switch frame and child `pt_regs`, clears PER/debug state, initializes timers and restart metadata, handles kernel threads separately, returns zero in the user child, optionally installs TLS in access registers 0/1, and clears the RI PSW bit for forked user threads. `__switch_to()` saves FPU/access/runtime-instrumentation/guarded-storage state, updates control registers for the next task, restores next state, then jumps to assembly switching.

State and persistence: per-task `thread_struct` owns kernel stack pointer, access registers, FPU state, PER state, timers, last-break address, RI and guarded-storage control blocks, and restart-block architecture data. No persistent external state is written.

Dependencies and integration points: depends on scheduler context switching, lowcore LPP updates, access-register and FPU helpers, runtime instrumentation, guarded storage, ptrace PER flags, unwind stack walking, randomization helpers, and s390 assembly entry code.

Risks: copy/switch ownership of RI and guarded-storage buffers is subtle; copying pointers would cause premature frees or cross-task state corruption. Kernel-thread frames must match `ret_from_fork` assembly expectations. `__switch_to()` must update control registers before restoring hardware state that depends on them. TLS is carried in access registers rather than an architecture-neutral slot.

Test signals: fork/clone with and without `CLONE_SETTLS`, kernel thread creation, exec clearing FPC, context-switch stress with FPU/VX/RI/guarded-storage users, ptrace single-step across forks, wait-channel reporting, and ASLR entropy for stacks and brk.

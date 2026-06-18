# sources/distributed-fs/ceph-client/arch/um/kernel/process.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/process.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/process.c

### Purpose
This file implements UML task switching, thread creation, idle behavior, exitcall execution, and wait-channel reporting.

### Important APIs, Types, And Functions
Key APIs include `cpu_tasks`, stack alloc/free, `__switch_to()`, `interrupt_end()`, `new_thread_handler()`, `copy_thread()`, `initial_thread_cb()`, `arch_dup_task_struct()`, idle hooks, `__uml_cant_sleep()`, `do_uml_exitcalls()`, `uml_strdup()`, `copy_from_user_proc()`, `singlestepping()`, `arch_align_stack()`, and `__get_wchan()`.

### Control Flow
Context switch updates the per-CPU current task, jumps between saved buffers, and invokes subarch switch code. Fork seeds either copied user registers or kernel-thread safe registers, creates a jump buffer targeting a fork/new-thread handler, optionally sets TLS, and eventually enters `userspace()`. `interrupt_end()` drains reschedule, signal, and notify work.

### State, Persistence, And Dependencies
State includes per-CPU current task pointers, per-task jump buffers/registers, task stacks, UML exitcall sections, and time-travel idle behavior. Dependencies include scheduler core, SKAS switching, subarch TLS/register helpers, signal handling, random stack alignment, and task stack helpers.

### Integration Points And Risks
Risks include jump-buffer corruption, init_task dynamic-size handling, TLS ordering, recursive scheduling in work-mask loops, and heuristic wait-channel stack scanning. Integration is central to all UML process and kernel-thread execution.

### Test Signals
Test fork/clone/kernel threads, exec, TLS, context switching under SMP, signals after interrupts, idle with time travel, UML exitcalls, and wait-channel reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/process.c -->

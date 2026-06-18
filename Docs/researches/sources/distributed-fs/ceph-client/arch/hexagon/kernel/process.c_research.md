# sources/distributed-fs/ceph-client/arch/hexagon/kernel/process.c

## Purpose

`process.c` implements Hexagon process and thread lifecycle hooks: userspace launch, idle, fork setup, wait-channel walking, and return-to-user pending work. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `start_thread`, `arch_cpu_idle`, `copy_thread`, `flush_thread`, `__get_wchan`, and `do_work_pending`. Concrete declarations observed in the file: Includes: `linux/cpu.h`, `linux/sched.h`, `linux/sched/debug.h`, `linux/sched/task.h`, `linux/sched/task_stack.h`, `linux/types.h`, `linux/module.h`, `linux/tick.h`, `linux/uaccess.h`, `linux/slab.h`, `linux/resume_user_mode.h`. Types referenced or declared: `pt_regs`, `task_struct`, `kernel_clone_args`, `thread_info`, `hexagon_switch_stack`. Functions/syscalls: `start_thread`, `arch_cpu_idle`, `copy_thread`, `flush_thread`, `do_work_pending`.

## Control Flow, State, And Persistence

Control flow covers ELF exec register reset, idle `__vmwait`, child kernel/user stack construction, scheduler wait-channel frame walking, and return-from-event handling of reschedule, signals, and notify-resume work.

## Dependencies And Integration Points

It depends on `pt_regs`, `thread_info`, scheduler/task APIs, Hexagon VM wait, and `ret_from_fork` from assembly.

## Risks And Test Signals

Risks are wrong child stack layout, TLS restore bugs, syscall restart interaction, and missed pending work. Test signals are fork/clone/TLS tests, kernel thread startup, scheduler traces, signal delivery, and idle tick behavior.
 A local static signal for this file is that it has 184 lines and 4777 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.

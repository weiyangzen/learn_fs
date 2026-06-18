<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/thread_info.h

Purpose: defines LoongArch low-level thread info layout, stack sizing, and TIF flags.
Important APIs and types: provides `struct thread_info`, `THREAD_SIZE`, `_THREAD_MASK`, `INIT_THREAD_INFO`, and flags such as `TIF_SYSCALL_TRACE`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_NOTIFY_SIGNAL`, `TIF_SINGLESTEP`, and watch/debug-related flags.
Control flow: entry/return assembly tests TIF flags to decide whether to deliver signals, reschedule, notify tracing/seccomp, or manage debug state.
State and persistence: thread flags and CPU/preempt fields persist in per-task low-level state and are frequently read from assembly.
Dependencies and integration: tied to kernel stack layout, `stackframe.h`, scheduler, signal code, ptrace, syscall work, hardware breakpoints, and assembly offsets.
Risks and test signals: flag-number drift or stack-size mistakes break return-to-user work and stack masking. Signals include scheduler stress, signal/syscall tracing, single-step, and stack overflow detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/thread_info.h -->

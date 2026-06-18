# sources/distributed-fs/ceph-client/arch/arm/kernel/process.c

Purpose: implements ARM process/thread lifecycle glue, idle hooks, register dumps, fork context setup, TLS propagation, wait-channel unwinding, gate VMA naming, and sigpage/vDSO mapping.

Important APIs/types/functions: `arch_cpu_idle*`, `show_regs`, `exit_thread`, `flush_thread`, `copy_thread`, `__get_wchan`, `arch_vma_name`, `arch_setup_additional_pages`, and gate-area helpers. It exports `thread_notify_head`, current task storage, and stack protector guard when configured.

Control flow: fork copies or initializes `pt_regs`, seeds `cpu_context` to `ret_from_fork`, clears ptrace hardware breakpoints, and handles TLS. Flush clears debug/fp/TLS state and notifies listeners. Sigpage setup allocates a randomized signal trampoline page and maps it with optional vDSO after exec.

State and persistence: per-thread CPU context, TLS values, debug state, fpstate, sigpage mapping in `mm->context.sigpage`, and optional global `signal_page`.

Dependencies and integration: scheduler, ptrace/hw breakpoints, thread notifiers, VFP/iWMMXt via fpstate, signal code, vDSO, memory management, gate VMA, LED triggers, and stacktrace.

Risks: bad child register setup breaks fork/clone; stale debug/fp state leaks across exec; sigpage mapping failures affect signal return. Test signals include fork/clone/TLS tests, `/proc/<pid>/maps` sigpage/vectors, signal return, register dumps on oops, and idle/resume behavior.

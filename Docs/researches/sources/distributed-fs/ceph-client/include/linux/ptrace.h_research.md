# sources/distributed-fs/ceph-client/include/linux/ptrace.h

Purpose: defines the generic in-kernel ptrace control surface: tracing flags, permission checks, task link/unlink helpers, event notification, syscall tracing reports, single-step/block-step arch hooks, and process memory access helpers.

Important APIs and types: `struct syscall_info` extends `seccomp_data` with stack pointer. Flags include `PT_PTRACED`, `PT_SEIZED`, trace event enables, `PT_EXITKILL`, and `PT_SUSPEND_SECCOMP`. Permission modes include read/attach and fscreds/realcreds combinations. APIs include `ptrace_access_vm()`, `arch_ptrace()`, data read/write helpers, `ptrace_disable()`, `ptrace_request()`, `ptrace_notify()`, link/unlink/exit helpers, `ptrace_may_access()`, generic peek/poke, `task_current_syscall()`, and compat sigaction ABI handling. Inline helpers cover `ptrace_parent()`, `ptrace_event_enabled()`, `ptrace_event()`, `ptrace_event_pid()`, `ptrace_init_task()`, `ptrace_release_task()`, syscall success handling, arch single-step fallbacks, `user_single_step_report()`, and syscall entry/exit reports.

Control flow: fork initializes ptrace fields and optionally links a traced child to the parent's tracer; event sites check enabled bits and call `ptrace_notify()`; syscall entry/exit work reports traps and may abort syscall entry; reaping releases ptrace links. Architecture code supplies request handling and stepping behavior where supported.

State and persistence: ptrace state lives in `task_struct`: flags, parent/real_parent relationships, ptraced lists, jobctl, pending signals, and ptracer credentials. It is runtime process-control state and ends with task lifetime.

Dependencies and integration points: depends on scheduler/task structures, signal delivery, pid namespaces, seccomp, credentials, UAPI ptrace constants, architecture register/syscall helpers, and process_vm-style memory access. It is a security-sensitive interface between debuggers/tracers and traced tasks.

Risks and test signals: risks include credential mode mistakes, ptrace parent namespace races in `ptrace_event_pid()`, signal/jobctl state bugs, single-step fallback misuse, syscall abort semantics, memory access permission bypass, and tasklist/RCU lifetime errors. Test ptrace attach/seize, fork/vfork/clone/exec/exit/seccomp events, pid namespaces, syscall tracing and emulation, single-step/block-step per architecture, process memory read/write, and LSM/Yama-style permission checks.

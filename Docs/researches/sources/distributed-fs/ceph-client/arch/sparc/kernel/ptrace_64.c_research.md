# sources/distributed-fs/ceph-client/arch/sparc/kernel/ptrace_64.c

Purpose: implements SPARC64 ptrace, compat ptrace, cache maintenance for ptrace page access, 64-bit and 32-bit user regsets, syscall trace/audit/seccomp hooks, and generic register lookup/stack helpers.

Important APIs/functions: public hooks are `ptrace_disable()`, `flush_ptrace_access()`, `task_user_regset_view()`, `compat_arch_ptrace()`, `arch_ptrace()`, `syscall_trace_enter()`, `syscall_trace_leave()`, `regs_query_register_offset()`, and `regs_get_kernel_stack_nth()`. Regset helpers cover native and compat general/FPU register views plus legacy GETREGS/GETFPREGS layouts.

Control flow: `flush_ptrace_access()` handles D-cache alias invalidation and pre-Cheetah I-cache flushes after `access_process_vm()` copies. Native regsets copy globals/out registers from `pt_regs`, read or write the user register window in 32-bit or biased 64-bit format, and restrict `tstate` writes to condition-code/syscall bits. FPU regsets save current FPU first, then expose lower/upper FP banks, FSR, GSR, and FPRS according to saved flags. Compat paths translate PSR/TSTATE and 32-bit register-window formats. Syscall enter runs strict seccomp, NOHZ user exit, ptrace entry, tracepoint, and audit; syscall leave runs audit, tracepoint, ptrace exit, and NOHZ user enter.

State and persistence: mutates task `pt_regs`, user register-window memory, per-thread FP/VIS state (`fpregs`, `xfsr`, `gsr`, `fpsaved`), and cache lines. Ptrace-visible state is task-local and core-dump-visible; no durable storage is written.

Dependencies and integration points: depends on generic ptrace/regset/compat ptrace APIs, seccomp, audit, syscall tracepoints, SPARC cache ASIs, VIS/FPU helpers, `psrcompat`, `access_process_vm()`, stack-bias conventions, and `thread_info` flags including `TIF_32BIT` and `TIF_NOHZ`.

Risks: cache alias handling is CPU-generation sensitive. Compat register-window setters contain pointer and position arithmetic that must preserve ABI behavior. Allowing only safe TSTATE bits is necessary to prevent privilege/control-state corruption. Syscall tracing order affects seccomp, audit, ptrace, and context tracking semantics.

Test signals: native and 32-bit compat gdb sessions, core dumps for `EM_SPARCV9` and `EM_SPARC`, ptrace text modification on aliasing-cache systems, syscall tracepoints/audit/seccomp ordering, FP/VIS register read-write tests, register offset lookup, and kernel stack nth-entry queries.

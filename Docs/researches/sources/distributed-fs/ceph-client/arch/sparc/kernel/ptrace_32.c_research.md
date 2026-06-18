# sources/distributed-fs/ceph-client/arch/sparc/kernel/ptrace_32.c

Purpose: implements 32-bit SPARC ptrace and core-dump register views for general registers, register windows, floating-point state, legacy ptrace requests, and syscall tracing.

Important APIs/functions: public hooks are `ptrace_disable()`, `task_user_regset_view()`, `arch_ptrace()`, and `syscall_trace()`. Regset helpers include `regwindow32_get/set()`, `genregs32_get/set()`, `fpregs32_get/set()`, `getregs_get()`, `setregs_set()`, `getfpregs_get()`, and `setfpregs_set()`.

Control flow: regset getters flush user windows for the current task, copy global/out registers from `pt_regs`, fetch locals/ins from the user register window using `copy_from_user()` or `access_process_vm()`, and append PSR/PC/NPC/Y. Setters copy incoming data back while restricting PSR writes to condition-code and syscall bits. Legacy `arch_ptrace()` maps SPARC requests such as `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETFPREGS`, `PTRACE_READTEXT`, and `PTRACE_WRITETEXT` onto regset or generic ptrace helpers, translating `PTRACE_SPARC_DETACH` to `PTRACE_DETACH`.

State and persistence: mutates stopped task `pt_regs`, user register-window memory, `thread.float_regs`, and `thread.fsr`. State is task-local and appears in ptrace/core-dump ABI; no persistent storage is written.

Dependencies and integration points: depends on generic ptrace/regset helpers, ELF notes (`PRSTATUS`, `PRFPREG`, `EM_SPARC`), SPARC register-window layout, `access_process_vm()`, FPU thread state, and syscall entry/exit tracing flags.

Risks: register-window access can fault if the saved user frame pointer is invalid. Regset layout is ABI and must match gdb/core expectations. The FPU save/clear calls are disabled with `#if 0`, so correctness relies on surrounding FPU ownership handling. Partial ptrace data copies must return `-EIO` consistently for legacy APIs.

Test signals: gdb attach/detach, `PTRACE_GETREGS/SETREGS`, FP register access, core dumps with SPARC regsets, text/data read-write ptrace operations, syscall tracing stops on entry/exit, and invalid user-window fault paths.

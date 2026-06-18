# sources/distributed-fs/ceph-client/arch/mips/kernel/ptrace.c

## Purpose
Implements native MIPS ptrace, user regset views, watchpoint access, FP/MSA/DSP regset access, register-name offset lookup, and syscall tracing entry/exit hooks.

## Important APIs, Types, and Functions
- `exception_ip()`, `ptrace_disable()`, `ptrace_getregs()`, and `ptrace_setregs()` expose basic exception PC and GPR access.
- `ptrace_get_watch_regs()` and `ptrace_set_watch_regs()` expose hardware watchpoint state with MIPS32/MIPS64 layouts.
- `gpr32_get/set()`, `gpr64_get/set()`, `fpr_get/set()`, `msa_get/set()`, `dsp32_get/set()`, `dsp64_get/set()`, and `fp_mode_get/set()` back ELF core/ptrace regsets.
- `task_user_regset_view()` chooses o32, n32, or n64 regset views from task flags.
- `regs_query_register_offset()` maps symbolic register names to `struct pt_regs` offsets.
- `arch_ptrace()` implements legacy ptrace requests.
- `syscall_trace_enter()` and `syscall_trace_leave()` integrate ptrace/seccomp/audit/tracepoints with syscall assembly paths.

## Control Flow
Native ptrace requests enter `arch_ptrace()`, which dispatches peek/poke memory to generic helpers, handles `PTRACE_PEEKUSR/POKEUSR` by switching on MIPS register numbers, delegates bulk GPR/FPR/watch requests, and falls back to `ptrace_request()`. Regset users call through selected `user_regset_view` based on task ABI flags. FPU setters initialize FP context before writes and mask FCSR writable bits. MSA getters pad unavailable vector lanes with all-ones fill and append control registers; setters mask exception/cause bits. Syscall assembly calls `syscall_trace_enter()` before dispatch when TIF flags require it; that function runs ptrace entry reporting, seccomp, tracepoints, audit, and negative-syscall cleanup. Exit tracing reports audit, tracepoints, ptrace exit, and re-enters user context tracking.

## State and Persistence
State resides in child task pt_regs, `thread.fpu`, `thread.dsp`, `thread.watch`, TIF flags, and `thread_info()->syscall`. Watchpoint load state is controlled through `TIF_LOAD_WATCH`. No persistent storage exists.

## Dependencies and Integration Points
Depends on generic ptrace/regset infrastructure, MIPS syscall helpers, audit, seccomp, ftrace syscall tracepoints, FPU/MSA/DSP/watch helpers, process FP mode functions, ELF note definitions, ABI flags, and syscall entry assembly. `process.c` provides register dump helpers and FP mode changes.

## Risks
ABI width and sign-extension behavior is subtle: GPR bulk access uses 64-bit formats for old native requests but regsets differ by view. Poking syscall registers must refresh `thread_info()->syscall`, including indirect syscall cases. FCSR/MSACSR masking prevents user injection of reserved exception bits. Watchpoint address validation differs for 32-bit address tasks on 64-bit kernels. The GPR set loops use `for (i = start; i < num_regs; i++)`, so partial writes must be reviewed carefully against intended `start + num_regs` semantics.

## Test Signals
`strace`, `gdb`, core dumps, and `PTRACE_GETREGSET/SETREGSET` should work for o32, n32, and n64 tasks. Hardware watchpoint tests should load/unload watch registers correctly. FP/MSA/DSP regset tests should preserve state and reject unavailable features with `-EIO`/`-ENODEV`. Seccomp and syscall tracepoints should skip or report syscalls exactly once.

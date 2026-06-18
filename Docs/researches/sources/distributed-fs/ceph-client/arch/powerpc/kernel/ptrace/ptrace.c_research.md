# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace.c

## Purpose
`ptrace.c` is the top-level PowerPC ptrace request dispatcher and syscall tracing hook implementation.

## Important APIs, Types, And Functions
It exports `ptrace_disable()`, `arch_ptrace()`, `do_syscall_trace_enter()`, `do_syscall_trace_leave()`, and `pt_regs_check()`. It uses `ptrace_get_reg()`, `ptrace_put_reg()`, FPR helpers, debug helpers, `copy_regset_to_user()`, `copy_regset_from_user()`, audit hooks, seccomp, and syscall tracepoints.

## Control Flow
`arch_ptrace()` handles USER-area peek/poke, hardware debug information and breakpoint commands, debugreg get/set, whole GPR/FPR/VMX/VSX/SPE regset requests, and delegates unknown requests to `ptrace_request()`. `do_syscall_trace_enter()` runs ptrace syscall-entry reporting, syscall emulation skipping, seccomp, syscall-number validation, tracepoints, and audit setup, returning either a valid syscall number or `-1` with `r3 = -ENOSYS`. `do_syscall_trace_leave()` records audit exit, tracepoint exit, and ptrace syscall-exit stops. `pt_regs_check()` is a build-time ABI assertion function.

## State And Persistence
The file manipulates task register state through helper functions and syscall trace flags. It does not store file-local persistent state.

## Dependencies And Integration Points
It integrates with generic Linux ptrace, seccomp, audit, trace/events/syscalls, PowerPC switch/debug helpers, native regset views, and compat handling through `ptrace32.c`.

## Risks
Syscall entry register semantics are ABI-sensitive, especially the difference between seccomp and ptrace use of `gpr[3]` and `orig_gpr3`. Invalid syscall handling must avoid audit/trace side effects. USER-area offsets and pt_regs layout must stay synchronized with UAPI constants.

## Test Signals
Run ptrace USER peek/poke tests, GET/SETREGS and feature regsets, seccomp trace/errno/allow paths, syscall emulation via `PTRACE_SYSEMU`, audit/tracepoint coverage, single-step detach behavior, and build failures from intentional pt_regs layout mismatches.

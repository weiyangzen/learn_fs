# sources/distributed-fs/ceph-client/arch/m68k/kernel/ptrace.c

## Purpose

`ptrace.c` implements m68k register access, single-step controls, syscall tracing hooks, and minimal ELF-FDPIC regset support for debuggers and core dumps.

## Important APIs, Types, and Functions

The file defines `ptrace_disable()`, `user_enable_single_step()`, `user_enable_block_step()` on MMU builds, `user_disable_single_step()`, `arch_ptrace()`, `syscall_trace_enter()`, `syscall_trace_leave()`, and optional `task_user_regset_view()`. Internal helpers `get_reg()` and `put_reg()` use `regoff[]` offsets into `pt_regs` and `switch_stack`, with `PT_USP` handled through `task->thread.usp`.

## Control Flow

`arch_ptrace()` handles legacy m68k requests: `PTRACE_PEEKUSR`, `PTRACE_POKEUSR`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, FPU register get/set, and `PTRACE_GET_THREAD_AREA`, then delegates unknown requests to `ptrace_request()`. It masks writable status-register bits with `SR_MASK` so user-space cannot set privileged SR state. Single-step control sets or clears trace bits `T1_BIT`/`T0_BIT` and `TIF_DELAYED_TRACE`. Syscall tracing reports entry before seccomp, lets `secure_computing()` veto the syscall, and reports exit afterward.

## State and Persistence Behavior

The code reads and writes saved register frames in the traced task, `thread.usp`, `thread.fp`, and thread flags. It does not persist external state, but debugger writes directly affect future execution of the traced task.

## Dependencies and Integration Points

It depends on exact process stack layout from `process.c` and entry assembly, status-register semantics, FPU emulator internal format, seccomp, generic ptrace, and ELF regset infrastructure. `ptrace.h` declares the syscall trace hooks for assembly.

## Risks and Edge Cases

Offsets must remain synchronized with `struct pt_regs` and `struct switch_stack`. `stkadj` handling for SR/PC is necessary for nonstandard exception frames; missing it would expose or overwrite the wrong return state. FPU emulator long-double conversion is ABI-sensitive. Seccomp and ptrace ordering must remain compatible with generic expectations.

## Test Signals

Run debugger tests for reading/writing all GPRs, SR masking, PC changes, single-step and block-step traps, syscall trace/seccomp interactions, FPU register access, TLS get, and FDPIC core dump note generation.

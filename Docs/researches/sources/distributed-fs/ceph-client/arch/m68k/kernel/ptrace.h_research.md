# sources/distributed-fs/ceph-client/arch/m68k/kernel/ptrace.h

## Purpose

`ptrace.h` is the private declaration header for m68k syscall tracing hooks used by low-level entry code.

## Important APIs, Types, and Functions

It declares `asmlinkage int syscall_trace_enter(void);` and `asmlinkage void syscall_trace_leave(void);`.

## Control Flow

There is no in-file control flow. Entry assembly calls `syscall_trace_enter()` before executing a syscall when tracing/seccomp work is pending, and calls `syscall_trace_leave()` on the way out.

## State and Persistence Behavior

The header owns no state. The declared functions operate on current task flags, pt_regs, ptrace, and seccomp state in `ptrace.c`.

## Dependencies and Integration Points

It depends on `<linux/linkage.h>` for the assembly-compatible calling convention. It integrates with `entry.S` and generic syscall tracing.

## Risks and Edge Cases

Changing return type or calling convention without matching entry assembly would corrupt syscall dispatch, especially because `syscall_trace_enter()` returns a value used to skip or continue syscall execution.

## Test Signals

Compile coverage and syscall tracing tests under `strace`, ptrace, and seccomp are sufficient.

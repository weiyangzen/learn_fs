# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace32.c

## Purpose
`ptrace32.c` implements compat ptrace handling for 32-bit tracers or tracees on a 64-bit PowerPC kernel, including special 32-to-64 USER-area commands.

## Important APIs, Types, And Functions
It exports `compat_arch_ptrace()`. Local macros `FPRNUMBER()`, `FPRHALF()`, and `FPRINDEX()` translate 32-bit FPR word indexes into `thread.fp_state` positions. It delegates many commands to `arch_ptrace()` or `compat_ptrace_request()`.

## Control Flow
The function handles 3264 memory peek/poke by reading a 32-bit pointer from the tracer and using `ptrace_access_vm()` against a 64-bit target address. It handles normal 32-bit USER peek/poke with 4-byte alignment and FPR word indexing, and 3264 USER peek/poke by selecting high or low halves of 64-bit registers. It has special legacy debugreg handling, then routes GET/SETREGS through the current task's regset view and delegates broader commands to native `arch_ptrace()`.

## State And Persistence
State changes are made through `ptrace_put_reg()`, direct FPR word updates after `flush_fp_to_thread()`, `ptrace_access_vm()` writes, and delegated breakpoint/register handlers.

## Dependencies And Integration Points
It is built under `CONFIG_COMPAT`, depends on `linux/compat.h`, and bridges old PPC32 ptrace ABIs with the shared native helper layer.

## Risks
The high/low half selection uses host memory layout for a temporary `u64`, so endian assumptions are important. Address arguments are mixed 32-bit userspace pointers and 64-bit target addresses. FPR indexing has legacy PPC32 semantics that differ from whole-regset access.

## Test Signals
Compat tests should cover PPC_PTRACE_PEEKTEXT_3264/POKETEXT_3264, PEEKUSR/POKEUSR for GPR and FPR halves, PEEKUSR_3264/POKEUSR_3264 high and low halves, GETREGS/SETREGS for 32-bit tasks, debugreg compatibility, and invalid alignment/out-of-range cases.

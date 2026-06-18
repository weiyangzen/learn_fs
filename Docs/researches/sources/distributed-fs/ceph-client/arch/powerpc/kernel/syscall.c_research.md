# sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscall.c

## Purpose
Implements the C-level PowerPC system call exception path from user mode into the syscall table.

## Important APIs, Types, and Functions
- `system_call_exception(struct pt_regs *regs, unsigned long r0)` is the central syscall dispatcher.
- Handles KUAP/KUEP/pkey register capture, context tracking, random kstack offset, tracing entry, TM syscall abort, syscall trace hooks, compat table dispatch, and nospec bounds barrier.

## Control Flow and State
The path locks KUAP, reconciles irq trace state, exits user context, randomizes kernel stack offset, validates user-mode entry assumptions, saves AMR/IAMR when pkeys are active, restores debug registers, accounts user/stolen time, prepares soft mask state, handles transactional-memory syscalls, enables IRQs, processes ptrace/seccomp tracing, validates syscall number, applies a speculation barrier, then calls the native or compat syscall table entry.

## State and Persistence Behavior
Mutates `pt_regs` saved pkey fields, thread flags (`_TIF_RESTOREALL` for TM), context tracking state, CPU accounting, IRQ soft-mask metadata, and potentially returns modified `regs->gpr[3]` when tracing rejects a syscall. TM transactional syscalls are doomed with `tabort` and return `-ENOSYS` internally.

## Dependencies and Integration Points
Integrates with entry assembly, KUAP/KUEP, context tracking, ptrace/seccomp syscall trace, compat syscall tables in `systbl.c`, transactional memory support in `tm.S`, BookE debug restoration, and syscall wrappers.

## Risks
This is a security-critical entry path. Incorrect AMR/IAMR handling can expose user access; wrong IRQ/context tracking state breaks lockdep/RCU; missing nospec barrier can expose syscall table speculation; TM handling must avoid returning via RFSCV to transactional state.

## Test Signals
Native and compat syscall smoke tests, ptrace/seccomp tracing, invalid syscall numbers, unsupported `scv` vector SIGILL, pkey/KUAP configurations, transactional-memory active syscalls, lockdep/RCU context tracking, and syscall fuzzers.

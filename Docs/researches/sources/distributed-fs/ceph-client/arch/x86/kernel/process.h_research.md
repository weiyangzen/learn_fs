# sources/distributed-fs/ceph-client/arch/x86/kernel/process.h

## Purpose
Provides shared inline context-switch glue for 32-bit and 64-bit x86 process code, keeping the common fast path cheap while deferring uncommon work to `__switch_to_xtra()`.

## APIs, Types, And Functions
Declares `__switch_to_xtra(struct task_struct *prev_p, struct task_struct *next_p)` and defines `switch_to_extra(struct task_struct *prev, struct task_struct *next)`.

## Control Flow
`switch_to_extra()` reads previous and next thread flags, optionally masks `_TIF_SPEC_IB` from both when conditional STIBP is disabled, and calls `__switch_to_xtra()` only if either task has context-switch work bits in `_TIF_WORK_CTXSW_NEXT` or `_TIF_WORK_CTXSW_PREV`.

## State And Persistence
No private state. It interprets per-task thread flags and static branch state from speculation-control code.

## Dependencies And Integration
Included by `process.c`, `process_32.c`, and `process_64.c`. Depends on task thread flag APIs and `switch_to_cond_stibp` from speculation-control support.

## Risks And Test Signals
The main risk is missing required extra work on context switch or calling it too often. Missing calls can leak debug, I/O bitmap, TSC, CPUID, or speculation state; excessive calls hurt scheduler performance. Test signals include context-switch microbenchmarks plus targeted tests for blockstep, I/O permission, CPUID/TSC prctl, and STIBP/SSBD transitions.

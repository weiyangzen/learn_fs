# sources/distributed-fs/ceph-client/arch/mips/kernel/r4k_switch.S

## Purpose
Implements R4K/newer low-level task switching through the `resume` assembly entry.

## Important APIs, Types, and Functions
- `resume(prev, next, next_ti)` saves previous task nonscratch state, restores next task state, updates stack tracking, CP0 status, and returns the previous task.

## Control Flow
The routine stores CP0 status and callee-saved registers into `prev`, stores RA, updates stack canary on supported !SMP builds, sets `$28` to the next thread_info pointer, restores `next` nonscratch registers, computes the top-of-thread kernel stack, calls `set_saved_sp`, merges current status low bits with `next` saved status, writes CP0 status, returns `prev` in `v0`, and jumps to restored RA.

## State and Persistence
Task state is persisted in `thread_struct` across scheduler switches. Per-CPU kernel stack tracking is updated by `set_saved_sp`. CP0 status changes are hardware state.

## Dependencies and Integration Points
Scheduler switch path, stackframe macros, thread-info offsets, stack protector, and MIPS interrupt/status conventions.

## Risks
Race-sensitive ordering of `$28`, stack pointer, and saved kernel SP must be preserved. Status masking must not leak FPU/kernel/user bits. Assembly offset mismatches would corrupt tasks.

## Test Signals
Heavy context-switch and preemption tests should preserve callee-saved registers, per-task status, stack protector canary, and return paths.

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/tm.S

## Purpose
Implements low-level PowerPC transactional memory helpers for enabling/disabling TM, saving/restoring TM SPRs, aborting transactions, reclaiming transactional state at context switch/signal paths, and recheckpointing saved state.

## Important APIs, Types, and Functions
- `tm_enable()`, `tm_disable()`, and `tm_abort(cause)` are exported helpers.
- `tm_save_sprs()`/`tm_restore_sprs()` move TFHAR/TEXASR/TFIAR between SPRs and `thread_struct`.
- `tm_reclaim(thread, cause)` aborts/reclaims a suspended transaction and saves checkpointed GPR/FPR/VMX/VSX/TAR/DSCR/AMR/PPR/TM SPR state into `thread_struct`.
- `__tm_recheckpoint(thread)` reloads checkpointed state and executes `TRECHKPT` so the task can resume with transactional state.

## Control Flow and State
`tm_reclaim` builds a special stack frame, enables FP/VMX/VSX with IRQs hard-off, verifies suspended state, clears recoverability while using scratch SPR/PACA-only accesses, executes `TRECLAIM`, reconstructs kernel PACA/SP, saves user checkpointed registers into `thread_struct`, saves FP/vector/TM SPR state, restores kernel AMR/MSR, and returns. `__tm_recheckpoint` loads checkpointed FP/vector/GPR/special state, performs sanity checks on TEXASR and MSR, temporarily stores user r1/r5/r13 on stack, clears RI, executes `TRECHKPT`, restores PACA/kernel state, and returns.

## State and Persistence Behavior
Mutates MSR TM/RI/FP/VEC/VSX bits, PACA scratch fields, `thread_struct` checkpointed and live TM fields, DSCR/PPR/AMR/TAR, and hardware TM SPRs. It must run with IRQs off and carefully avoids faults while RI is clear.

## Dependencies and Integration Points
Coupled to signal TM handling in `signal_64.c`, context switch code, `thread_struct` offsets, PACA layout, FPU/VMX/VSX save macros, TM opcodes, feature fixups, and exported helpers used by modules/kernel code.

## Risks
Extremely sensitive to register clobbering, stack layout, recoverability, and fault avoidance. Bugs can corrupt user transactions, kernel PACA state, or make unrecoverable exceptions. Requires matching C structure offsets and CPU TM feature behavior.

## Test Signals
TM userspace stress with signals, preemption, context switches, ptrace, FP/VMX/VSX inside transactions, syscall aborts, suspended transactions, and invalid CPU feature configs. Add lockdep/RCU/watchdog coverage for IRQ-off reclaim/recheckpoint durations.

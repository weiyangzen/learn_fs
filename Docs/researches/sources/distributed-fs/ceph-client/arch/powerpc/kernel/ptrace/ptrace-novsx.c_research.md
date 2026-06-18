# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-novsx.c

## Purpose
This file implements whole-FPR regset get/set for configurations without VSX.

## Important APIs, Types, And Functions
It exports `fpr_get()` and `fpr_set()`. It uses `struct thread_fp_state`, `flush_fp_to_thread()`, `membuf_write()`, `user_regset_copyin()`, and `empty_zero_page`.

## Control Flow
When FPU registers exist, both functions assert that `fpscr` follows `fpr[32]`, flush live FP state, and copy the contiguous 33-u64 FPR/FPSCR block out of or into `target->thread.fp_state`. Without FPU registers, get returns zeros and set succeeds without changing state.

## State And Persistence
The only persistent state touched is `thread.fp_state`.

## Dependencies And Integration Points
The Makefile builds this when `CONFIG_VSX` is not enabled. `ptrace-view.c` references these symbols for `REGSET_FPR` in native and compat views.

## Risks
The contiguous layout assumption is enforced by `BUILD_BUG_ON`; if the structure changes, this file must change with it. No-FPU behavior intentionally preserves ABI shape by returning zeros.

## Test Signals
Regset tests should verify FPR/FPSCR round trips, partial copy offsets, no-FPU zero behavior, and coredump PRFPREG note size.

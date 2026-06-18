# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_preempt.h

## Purpose

`a6xx_preempt.h` provides inline helpers for the A6xx/A8xx preemption state machine, deferred write-pointer updates, and next-ring selection. The helpers are shared by both preemption implementations and are deliberately small enough to inline into hot interrupt/submit paths.

## Important APIs, Types, And Functions

`try_preempt_state()` performs an atomic compare/exchange on `a6xx_gpu->preempt_state`. `set_preempt_state()` force-sets the state with barriers before and after the atomic store. `update_wptr()` writes a deferred ring WPTR to `REG_A6XX_CP_RB_WPTR` when `ring->restore_wptr` is set. `get_next_ring()` scans rings in priority order and returns the first non-empty candidate.

## Control Flow

The trigger path calls `try_preempt_state(PREEMPT_NONE, PREEMPT_START)` to claim preemption evaluation. IRQ paths call `try_preempt_state(PREEMPT_TRIGGERED, PREEMPT_PENDING)` to accept completions only for in-flight switches. `update_wptr()` locks the ring, checks the deferred flag, fetches `get_wptr(ring)`, uses `a6xx_fenced_write()`, then clears the flag. `get_next_ring()` locks each ring long enough to compare WPTR and RPTR. For the current ring, it treats the ring as empty when `memptrs->fence` matches `a6xx_gpu->last_seqno[i]`.

## State And Persistence Behavior

The helpers manipulate only existing persistent state: atomic `preempt_state`, per-ring `preempt_lock`, ring `restore_wptr`, ring memptr fence/context fields, and current-ring metadata. Memory ordering is explicit because state is observed across submission, IRQ, timer, and recovery contexts.

## Dependencies And Integration Points

Both `a6xx_preempt.c` and `a8xx_preempt.c` include this header. It depends on `a6xx_gpu.h` for `enum a6xx_preempt_state`, `struct a6xx_gpu`, register definitions, `shadowptr()`, and `a6xx_fenced_write()`. `get_next_ring()` relies on `gpu->funcs->get_rptr()` and the DRM/MSM ringbuffer model.

## Risks

The helpers assume the caller has selected the correct generation-specific register set for context switch control; only WPTR uses the shared A6xx register. `set_preempt_state()` can force transitions, so callers must use it only when they have already excluded competing transitions. `get_next_ring()` priority is fixed by ring index and may starve lower-priority rings under sustained higher-priority load.

## Test Signals

Tests should exercise concurrent submissions while preemption is being triggered, ring priority selection, deferred WPTR restore, current-ring empty detection by fence sequence, and state transitions under normal IRQ and timeout recovery paths.

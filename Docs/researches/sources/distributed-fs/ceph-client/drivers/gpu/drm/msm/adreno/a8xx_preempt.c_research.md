# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a8xx_preempt.c

## Purpose

`a8xx_preempt.c` is the A8xx register variant of the A6xx preemption implementation. It reuses the shared preemption state machine and per-ring records but writes A8xx context-switch registers, keepalive register, and postamble performance-counter registers.

## Important APIs, Types, And Functions

Public functions are `a8xx_preempt_hw_init()`, `a8xx_preempt_trigger()`, and `a8xx_preempt_irq()`. Local helpers are `preempt_prepare_postamble()`, `preempt_disable_postamble()`, and `a8xx_preempt_keepalive_vote()`. It uses `try_preempt_state()`, `set_preempt_state()`, `update_wptr()`, and `get_next_ring()` from `a6xx_preempt.h`.

## Control Flow

`a8xx_preempt_hw_init()` skips single-ring GPUs, resets each preemption record's ring pointers, SMMU/ring metadata, writes zero to `REG_A8XX_CP_CONTEXT_SWITCH_SMMU_INFO`, enables GMEM save/restore, resets state, initializes `eval_lock`, and sets ring 0 as current.

`a8xx_preempt_trigger()` follows the same sequence as A6xx: claim `PREEMPT_NONE -> PREEMPT_START`, build context switch control with A8xx bitfields, choose the next non-empty ring, bail out with WPTR refresh when no switch is needed, update target SMMU info and record WPTR under ring lock, clear `restore_wptr`, vote A8xx preempt keepalive on, fenced-write A8xx SMMU and restore-record addresses, set `next_ring`, arm a 10-second timer, enable/disable postamble based on sysprof state, set `PREEMPT_TRIGGERED`, and fenced-write `REG_A8XX_CP_CONTEXT_SWITCH_CNTL`.

`a8xx_preempt_irq()` accepts only a triggered preemption, cancels the timer, checks `REG_A8XX_CP_CONTEXT_SWITCH_CNTL` STOP bit, queues recovery on failure, otherwise swaps `cur_ring`, clears `next_ring`, refreshes deferred WPTR, resets state, turns keepalive off, traces completion, and retriggers.

## State And Persistence Behavior

State is stored in shared `struct a6xx_gpu` fields: preemption records, SMMU info, current/next rings, postamble buffer, preempt timer, atomic preempt state, and flags for save/restore/GMEM. The keepalive vote persists in the A8xx GMU until explicitly cleared at IRQ completion or recovery.

## Dependencies And Integration Points

`a8xx_gpu.c` calls `a8xx_preempt_hw_init()` during hardware initialization, `a8xx_irq()` dispatches CP SW interrupts to `a8xx_preempt_irq()`, and retire/cache flush interrupts call `a8xx_preempt_trigger()`. Shared allocation for records is still handled by `a6xx_preempt_init()`, so A8xx depends on common preempt setup.

## Risks

This file is structurally duplicated from `a6xx_preempt.c`, so future bug fixes can diverge. A wrong generation-specific register or bitfield would break only A8xx context switches. There is no wrapper-GMU skip in `a8xx_preempt_keepalive_vote()`, unlike A6xx, so that assumption must match all A8xx supported devices. STOP-bit failure paths leave cleanup to recovery.

## Test Signals

Expected signals are normal CP SW completion interrupts, tracepoint trigger/IRQ pairs, no preemption watchdog timeouts, correct switching under multi-ring submissions, reliable sysprof postamble toggling with A8xx perf-counter registers, and successful recovery when STOP remains set.

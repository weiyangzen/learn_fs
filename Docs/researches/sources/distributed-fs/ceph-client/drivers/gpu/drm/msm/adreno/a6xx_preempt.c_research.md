# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_preempt.c

## Purpose

`a6xx_preempt.c` implements ringbuffer preemption for A6xx-style Adreno GPUs with more than one DRM scheduler ring. It allocates per-ring preemption records and SMMU context buffers, initializes hardware state, triggers context switches, handles completion interrupts, updates ring write pointers, and recovers from stuck or failed preemption.

## Important APIs, Types, And Functions

Public functions are `a6xx_preempt_init()`, `a6xx_preempt_hw_init()`, `a6xx_preempt_trigger()`, `a6xx_preempt_irq()`, and `a6xx_preempt_fini()`. Local helpers include the watchdog `a6xx_preempt_timer()`, postamble builders `preempt_prepare_postamble()` and `preempt_disable_postamble()`, keepalive voting via `a6xx_preempt_keepalive_vote()`, and `preempt_init_ring()`.

The implementation depends on shared inline helpers from `a6xx_preempt.h`: `try_preempt_state()`, `set_preempt_state()`, `update_wptr()`, and `get_next_ring()`. It uses `struct a6xx_preempt_record` and `struct a7xx_cp_smmu_info` from `a6xx_gpu.h`.

## Control Flow

Initialization exits early for single-ring GPUs. For each ring, `preempt_init_ring()` allocates a write-combined private GEM BO for the preemption record and another GPU-readonly BO for SMMU info. It writes default ring base, RB control, magic values, TTBR/context defaults, and BV rptr address, then allocates a postamble BO and sets up a watchdog timer. Any allocation failure disables preemption by cleaning up and forcing `gpu->nr_rings = 1`.

Hardware init resets per-ring records, writes zero to `REG_A6XX_CP_CONTEXT_SWITCH_SMMU_INFO`, enables GMEM save/restore, resets the atomic preemption state to `PREEMPT_NONE`, initializes the evaluation lock, and starts on ring 0.

`a6xx_preempt_trigger()` serializes candidate evaluation with `eval_lock`, transitions `PREEMPT_NONE -> PREEMPT_START`, computes `CP_CONTEXT_SWITCH_CNTL`, and asks `get_next_ring()` for the highest-priority non-empty ring. If no switch is needed, it refreshes the current ring WPTR and returns to `PREEMPT_NONE`. Otherwise it updates the target ring's SMMU info and preemption record under `ring->preempt_lock`, clears `restore_wptr`, votes keepalive on, fenced-writes target SMMU and restore-record addresses, records `next_ring`, starts a 10-second watchdog, toggles the postamble depending on sysprof state, transitions to `PREEMPT_TRIGGERED`, and writes context-switch control.

`a6xx_preempt_irq()` transitions `PREEMPT_TRIGGERED -> PREEMPT_PENDING`, cancels the watchdog, verifies the STOP bit cleared, installs `next_ring` as `cur_ring`, updates deferred WPTR state, returns to `PREEMPT_NONE`, votes keepalive off, traces completion, and retriggers to catch skipped requests.

## State And Persistence Behavior

Persistent state is in `a6xx_gpu`: atomic `preempt_state`, `cur_ring`, `next_ring`, per-ring record BO pointers/IOVAs, per-ring SMMU-info BOs/IOVAs, postamble BO/IOVA/length, `postamble_enabled`, feature flags `preempt_level`, `uses_gmem`, `skip_save_restore`, `eval_lock`, and `preempt_timer`. Each ring stores `restore_wptr` and memptr TTBR/context fields used during switch setup.

## Dependencies And Integration Points

`a6xx_gpu.c` calls preemption during GPU init, IRQ handling, retire events, and submissions. Register writes use `a6xx_fenced_write()` so CP-visible writes are sequenced. GMU keepalive prevents power collapse while a context switch is in flight. Tracepoints expose trigger and completion events. Recovery uses `gpu->worker` and `recover_work`.

## Risks

The state machine is race-sensitive. Missed barriers or unprotected WPTR updates can lose submissions or double-write ring pointers. The watchdog forces recovery after 10 seconds, but if recovery cannot run the GPU may remain stuck with keepalive asserted. `a6xx_preempt_fini()` only frees `preempt_bo[]` and not the SMMU/postamble BOs in this file, so ownership must be checked in wider teardown. The A6xx and A8xx implementations are near-duplicates, making drift likely.

## Test Signals

Key signals are successful multi-ring scheduling under load, tracepoint pairs for trigger/irq, no preemption timeout logs, correct recovery when STOP remains set, no lost fences when switching away from or back to the current ring, and stable behavior when sysprof enables/disables postamble handling.

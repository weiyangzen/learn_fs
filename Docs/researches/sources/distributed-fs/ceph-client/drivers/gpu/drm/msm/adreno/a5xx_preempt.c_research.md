# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_preempt.c

## Purpose
`a5xx_preempt.c` implements A5xx multi-ring hardware preemption. It allocates per-ring preemption records, maintains a lockless atomic state machine, chooses the highest-priority runnable ring, triggers CP context switches, handles completion interrupts, and recovers from timeouts.

## Important APIs, Types, And Functions
Exported functions are `a5xx_preempt_init`, `a5xx_preempt_fini`, `a5xx_preempt_hw_init`, `a5xx_preempt_trigger`, and `a5xx_preempt_irq`. Private helpers include `try_preempt_state`, `set_preempt_state`, `update_wptr`, `get_next_ring`, `a5xx_preempt_timer`, and `preempt_init_ring`.

## Control Flow
Initialization exits for single-ring GPUs. For each ring it allocates a privileged preempt record BO plus an unprivileged counter BO, names them, fills the record magic, default RB control, and counter IOVA, then initializes the start lock and watchdog timer. Hardware init resets current ring to ring 0, initializes per-ring record fields with ring base and rptr shadow addresses, writes zero SMMU switch info, and sets state to `PREEMPT_NONE`.

Trigger flow serializes with `preempt_start_lock`, atomically moves `NONE` to `START`, finds the first non-empty ring, aborts back to `NONE` if no switch is needed while updating current WPTR, or records the incoming ring WPTR, writes restore record address, sets `next_ring`, arms a 10-second watchdog, sets `TRIGGERED`, and writes `CP_CONTEXT_SWITCH_CNTL`. IRQ flow moves `TRIGGERED` to `PENDING`, deletes the timer, verifies hardware cleared switch control, updates `cur_ring`, writes the new WPTR, returns to `NONE`, and retriggers to catch queued work.

## State And Persistence
Persistent state lives in `struct a5xx_gpu`: per-ring preempt/counter BOs, record pointers, IOVAs, current/next rings, atomic preempt state, start lock, and timer. Records persist across switches and are shared with CP microcode.

## Dependencies And Integration Points
The file depends on MSM GEM kernel BO helpers, ringbuffer locking and memptrs, `gpu->funcs->get_rptr`, A5xx context-switch registers, and the GPU worker recovery path. `a5xx_gpu.c` calls preempt init, hardware init, trigger on submit/retire, IRQ handler on CP_SW, and fini during destroy.

## Risks
Concurrency is the main risk. Submit and IRQ paths can race with preemption state, so barriers and the `PREEMPT_ABORT` intermediate state are important. A stuck hardware switch queues recovery through the watchdog. If `WHERE_AM_I` shadow support is absent, multi-ring preemption is disabled by the firmware load path. Resource allocation failure degrades to one ring.

## Test Signals
Signals include four-ring GPUs allocating records, ring priority switching under mixed workloads, CP_SW interrupts completing switches, watchdog recovery on forced timeout, no WPTR loss when submit races with abort, valid preempt counters, and clean fallback to one ring on allocation or firmware capability failure.

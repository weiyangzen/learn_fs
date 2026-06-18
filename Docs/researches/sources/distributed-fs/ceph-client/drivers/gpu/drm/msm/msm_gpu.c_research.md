# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu.c

## Purpose
Provides the common MSM GPU core: runtime power sequencing, register/IRQ setup, ringbuffer creation, command submission and retirement, hang detection/recovery, crash-state capture, devcoredump plumbing, performance counter sampling, and common GPU initialization/cleanup used by Adreno generation-specific implementations.

## Important APIs, Types, and Functions
- `msm_gpu_pm_resume()` and `msm_gpu_pm_suspend()` enable/disable regulators, clocks, AXI clock, and devfreq.
- `msm_gpu_hw_init()` invokes the generation-specific `gpu->funcs->hw_init()` with IRQ disabled when `needs_hw_init` is set.
- `msm_gpu_submit()` transitions the device active, initializes hardware, adds submit to the ring in-flight list, updates devfreq active state, calls the generation-specific submit hook, and arms hangcheck.
- `msm_gpu_retire()`, `retire_submits()`, and `retire_submit()` update fence contexts, release BO refs, update context elapsed/cycle accounting, and transition to idle.
- `hangcheck_handler()` detects lack of fence progress; `recover_worker()` captures diagnostics, advances fences, recovers hardware, and replays remaining submits.
- `msm_gpu_fault_crashstate_capture()` handles IOMMU fault crash dump capture.
- `msm_gpu_perfcntr_start()`, `msm_gpu_perfcntr_stop()`, and `msm_gpu_perfcntr_sample()` expose software and hardware perf sampling.
- `msm_gpu_create_private_vm()`, `msm_gpu_init()`, and `msm_gpu_cleanup()` manage common GPU resources.

## Control Flow
Initialization creates a kthread worker, initializes locks/work/timers, maps MMIO, requests IRQ, obtains clocks/regulators, initializes devfreq, creates the GPU VM, allocates memptrs, and creates ringbuffers. Runtime submit happens through the DRM scheduler backend in `msm_ringbuffer.c`, which calls `msm_gpu_submit()` under `gpu->lock`. Hardware completion updates ring memptr fences; IRQs call generation-specific handlers and schedule retirement. Hangcheck samples active ring fence progress and queues recovery if no progress. Recovery identifies the offending submit, marks fault counters and VM state, captures RD and devcoredump data, advances fences to unblock waiters, calls generation-specific recovery, and replays remaining submits unless their VM is unusable.

## State and Persistence
Persistent in-memory state is `struct msm_gpu`: rings, global VM, MMIO, clocks/regulators, worker, hangcheck timer, perf counters, devfreq, crashstate, active submit count, sysprof refcount, and fault counters. Per-context elapsed time and cycles are updated on retire. Crashstate persists until consumed/released by devcoredump. No on-disk persistence exists.

## Dependencies and Integration Points
Depends on generation-specific `msm_gpu_funcs`, MSM GEM submit/VMA/MMU/fence helpers, DRM scheduler ringbuffers, runtime PM, OPP/devfreq, Linux devcoredump, kthread workers, IRQ APIs, and tracepoints. It integrates with IOMMU page-table diagnostics by calling `msm_iommu_pagetable_params()` and `msm_iommu_pagetable_walk()` for fault captures.

## Risks
High-risk areas include recovery correctness, fence advancement on hangs, replaying submits after reset, power-management balance, crash capture under memory pressure, and synchronization between IRQ, worker, scheduler, and hangcheck timer. The code uses `gpu->lock`, `active_lock`, `submit_lock`, `perf_lock`, memalloc noreclaim sections, and runtime PM gets/puts to control those races.

## Test Signals
Signals include successful probe/remove, runtime suspend/resume, submit/retire tracepoints, correct fdinfo elapsed/cycle accounting, devcoredump content after forced hangs, IOMMU fault capture with ptes, no PM ref leaks, hangcheck recovery replaying later submits, and no stale in-flight submits after ring fence advancement.

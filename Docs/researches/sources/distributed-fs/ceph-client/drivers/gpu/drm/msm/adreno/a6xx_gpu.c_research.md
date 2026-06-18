# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gpu.c

## Purpose

`a6xx_gpu.c` is the main Adreno A6xx-family GPU implementation. It binds the GPU object, loads SQE/AQE firmware, initializes registers and CP state, emits command streams for A6xx and A7xx/A8xx submissions, manages runtime PM through the GMU, handles IRQs/faults/recovery, configures LLCC/system cache, performs bus halt/reset operations, exposes devfreq hooks, and registers the `adreno_gpu_funcs` tables for A6xx, wrapper, A7xx, and A8xx variants.

## Important APIs, Types, And Functions

- `a6xx_gpu_init()` allocates `struct a6xx_gpu`, detects GMU wrapper mode, initializes LLCC and supported OPP hardware, initializes the generic Adreno core, binds GMU, installs MMU fault handling, computes UBWC config, and initializes preemption.
- `a6xx_hw_init()` wraps `hw_init()` with `gmu->lock`. `hw_init()` programs GBIF/VBIF, security, address modes, HWCG, QoS, UCHE/GMEM, CP mempool, performance counters, UBWC, fault detection, CP protection, APRIV, interrupts, SQE/RB registers, preemption, CP init, and secure-mode exit.
- `a6xx_submit()` emits A6xx ring commands for pagetable switch, stats capture, IB execution, scratch fence, cache flush timestamp, trace, and flush.
- `a7xx_submit()` emits the generation 7 path with BR/BV thread control, IFPC markers, optional pseudo-reg/preemption state, BV fence synchronization, command-completion yield, and preempt trigger.
- `a6xx_set_pagetable()` emits SMMU table update packets and UCHE/perfcounter synchronization when a submit's context changes.
- `a6xx_flush()` updates shadow read pointers, updates ring `cur`, and fenced-writes `CP_RB_WPTR` if the ring is active and not currently preempting.
- `a6xx_irq()` decodes RBBM interrupts, keeps GMU alive while reading/clearing status, handles faults, CP errors, SW fuse violations, retirements, and preemption IRQs.
- `a6xx_recover()` coordinates crash recovery with runtime PM and CX power collapse.
- `a6xx_gmu_pm_resume()/suspend()` and `a6xx_pm_resume()/suspend()` implement full GMU and wrapper PM paths.
- `a6xx_gpu_busy()`, `a6xx_gpu_set_freq()`, `a6xx_get_rptr()`, and `a6xx_progress()` implement devfreq and scheduler integration.

## Control Flow

Probe calls `a6xx_gpu_init()` through the selected `adreno_gpu_funcs`. It allocates the object, initializes locks, reads the `qcom,gmu` phandle, initializes LLCC slices before OPP filtering, enables up to four rings if preemption is allowed, runs generic Adreno init, records speedbin, initializes the GMU full or wrapper path, installs the MMU fault handler, calculates UBWC settings, and sets up preemption records.

Runtime resume begins in the function table PM callback. Full GMU targets call `a6xx_gmu_resume()` under `gmu->lock`, resume devfreq, and activate LLCC slices. Wrapper targets set OPP/clock/domain state directly. The first submit or explicit core path later calls `a6xx_hw_init()`, which holds `GMU_OOB_GPU_SET` on full GMU targets so firmware does not power-collapse registers while Linux programs the GPU. The sequence ends by yielding preemption state, clearing OOB votes, and optionally setting perfcounter OOB for sysprof.

Submissions are ringbuffer packet construction. Both submit paths switch pagetables only when context sequence changes, write performance counters to memstore, emit user IBs while periodically updating shadow RPTR visibility, write a seqno fence, emit cache-clean/flush timestamp events, trace, and flush the ring. A7xx/A8xx adds BR/BV threading and separate BV fence wait so BR does not signal completion before BV finishes.

IRQs use `a6xx_gpu_keepalive_vote()` and `irq_poll_fence()` before reading `RBBM_INT_0_STATUS`. Hang-detect interrupts queue recovery after disabling GPU interrupts and deleting hangcheck. Cache flush timestamp retires completed submits and may trigger preemption. CP software interrupts service preemption completion. Severe CP and fuse errors log details and can queue recovery.

Recovery dumps Adreno info, halts SQE if GX is on, optionally dumps registers, marks the GPU hung, disables autosuspend, temporarily zeros active submit count, forces wrapper/RGMU bus halt and reset, asks genpd to power off CX, drops runtime PM refs to collapse hardware, waits for `pd_gate`, restores active submit count, resumes runtime PM, reinitializes hardware, and clears `hung`.

## State And Persistence Behavior

`struct a6xx_gpu` stores SQE/AQE BOs and IOVAs, current/next ring pointers, per-ring preemption records and SMMU info, last seqnos, preemption state/timer/locks, postamble BO, embedded `struct a6xx_gmu`, shadow RPTR BO, A7xx power-up reglist BO, LLCC state, hang flags, aperture state, and A8xx slice mask. BOs live across runtime suspend and are released in `a6xx_destroy()`. Runtime suspend clears shadow RPTR memory so ring state is re-established on next init.

Hardware state is mostly volatile and rebuilt by `hw_init()` after GMU resume or recovery. `pwrup_reglist_emitted` prevents regenerating A7xx power-up register lists after the initial capture. `cur_ring`, ring `cur_ctx_seqno`, `last_cp_state`, and `last_seqno` track scheduler/preemption progress.

## Dependencies And Integration Points

This file integrates with the DRM msm GPU scheduler, GEM/VM helpers, Adreno common code, generated register/enumeration/perfcounter headers, GMU/HFI code, preemption helpers, A8xx helpers, Linux OPP/devfreq, runtime PM, power domains, LLCC, IOMMU page-table code, UBWC common config, zap shader secure firmware, SCM-secure initialization through GMU code, and crash-state callbacks under `CONFIG_DRM_MSM_GPU_STATE`.

## Risks And Edge Cases

- Fenced register writes must work when GMU/IFPC can power-collapse GX. Timeouts around `GMU_AHB_FENCE_STATUS` can leave RB write pointers stale.
- `hw_init()` is a long generation-specific register script. Small ordering mistakes can break secure mode, CP init, IFPC, UBWC, or preemption.
- A7xx BR/BV synchronization is subtle; missing thread control or BV fence wait can signal completion before all work is done.
- Recovery manipulates runtime PM and `active_submits` intentionally. Imbalance can deadlock suspend, skip CX collapse, or lose active-submit refs.
- `a6xx_progress()` lies when IFPC is enabled because GX registers cannot be read safely. Hang detection hardware must be trusted in that mode.
- Firmware version gating rejects old SQE images on A630/A650. Unknown firmware names currently fail with `-EPERM`.
- Wrapper/full GMU function tables differ in PM and timestamp behavior; selecting the wrong table breaks clocks, OPP voting, or GMU firmware expectations.

## Test Signals

Important signals are successful SQE/AQE BO creation, CP init returning idle, zap shader success or expected `-ENODEV` fallback, working suspend/resume, ring fences retiring, preemption on multi-ring workloads, no fenced-write timeout logs, no CP protected mode/opcode errors, GPU busy counters changing under load, devfreq frequency changes, MMU faults reporting useful block names, recovery completing and resuming submissions, and devcoredump support calling `a6xx_gpu_state_get()` without wedging the GPU.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a8xx_gpu.c

## Purpose

`a8xx_gpu.c` implements generation-8 Adreno GPU operations plugged into the shared MSM/Adreno GPU framework. It covers aperture-controlled pipe/slice register access, slice discovery, idle/flush behavior, hardware clock gating, CP register protection, UBWC and non-context register programming, CP/power-up initialization, full hardware bring-up, recovery, fault decoding, interrupt handling, LLCC activation, bus halt, timestamp, busy counters, and progress reporting.

## Important APIs, Types, And Functions

Externally used functions include `a8xx_gpu_get_slice_info()`, `a8xx_flush()`, `a8xx_hw_init()`, `a8xx_recover()`, `a8xx_fault_handler()`, `a8xx_irq()`, `a8xx_llc_activate()`, `a8xx_bus_clear_pending_transactions()`, `a8xx_gmu_get_timestamp()`, `a8xx_gpu_busy()`, and `a8xx_progress()`.

Important local helpers are the aperture helpers (`a8xx_aperture_slice_set/acquire/release/clear`, `a8xx_write_pipe()`, `a8xx_read_pipe_slice()`), `a8xx_idle()`, `a8xx_set_hwcg()`, `a8xx_set_cp_protect()`, `a8xx_set_ubwc_config()`, `a8xx_nonctxt_config()`, `a8xx_patch_pwrup_reglist()`, `a8xx_preempt_start()`, `a8xx_cp_init()`, `hw_init()`, fault-block decoders, CP fault IRQ handling, hang-detect IRQ handling, and SW fuse handling.

## Control Flow

Pipe-specific register access is serialized through `a6xx_gpu->aperture_lock` and `REG_A8XX_CP_APERTURE_CNTL_HOST`; the cached aperture value avoids redundant writes. Slice discovery starts from catalog `max_slices`, masks with `REG_A8XX_CX_MISC_SLICE_ENABLE_FINAL` for Gen2+, and updates chip ID/name to encode active slice count.

`a8xx_hw_init()` takes the GMU lock and calls `hw_init()`. The bring-up sequence asserts GMU OOB GPU ownership, clears cached aperture and bus halts, disables secure memory ranges, programs GMEM/trap/UBWC/perf counters, emits non-context register lists, enables fault detection, configures GMU busy counters, programs CP protection, enables GMEM save/restore, masks per-pipe/global interrupts, calls `adreno_hw_init()`, programs SQE/AQE firmware bases and ringbuffer registers, calls `a8xx_preempt_hw_init()`, starts SQE, sends CP init packets, exits secure mode via zap shader or SECVID fallback, writes GMEM protection after non-secure transition, patches the power-up register list once, enables hardware clock gating, yields the ringbuffer for preemption, clears GMU OOB, and restores perf-counter OOB if sysprof is active.

Flush behavior is preemption-aware: it copies `ring->next` to `ring->cur`, computes WPTR, fenced-writes WPTR only if the ring is current and no preemption is active, otherwise marks `restore_wptr` for the preemption completion path.

Interrupt flow reads/clears `REG_A8XX_RBBM_INT_0_STATUS`, optionally filters error IRQs, dispatches hang detect, AHB, CP HW errors, ATB, UCHE, SW fuse, retire/cache flush, and CP SW preemption completion. Fatal paths disable interrupts and queue recovery.

Recovery marks the GPU hung, halts SQE, temporarily hides active submits from runtime suspend warnings, forces CX power-domain collapse through genpd notification, rebalances runtime PM refs, reinitializes hardware, and clears `hung`.

## State And Persistence Behavior

Persistent state includes `cached_aperture`, `slice_mask`, `pwrup_reglist_ptr` contents and `pwrup_reglist_emitted`, `cur_ring`, per-ring shadow values, runtime PM active submit counts during recovery, GMU status bits, and LLCC slice activation state. Register programming persists in hardware until reset or power collapse. The pwrup reglist stores IFPC/preemption register restore pairs plus dynamic aperture/address/data triplets for CP restoration.

## Dependencies And Integration Points

`a6xx_gpu.c` installs these callbacks in `a8xx_gpu_funcs`. The file integrates with GMU OOB and power counters, LLCC, qcom UBWC config, firmware loading/zap shader, DRM scheduler rings, MSM fault handling, A8xx preemption, runtime PM/genpd, and catalog register lists/protection tables.

## Risks

Aperture selection is global hardware state; missing release/clear or stale cache can direct reads/writes to the wrong pipe/slice. Bring-up order is fragile around secure-mode exit, GMEM protection, CP init, SQE start, and GMU OOB ownership. Recovery manipulates runtime PM refs and `active_submits`; imbalance can deadlock suspend/resume. `a8xx_progress()` always returns true, reducing hangcheck usefulness. Many register constants are hardware magic values with limited software validation.

## Test Signals

Signals include successful boot across A8xx variants, correct active-slice chip name updates, clean idle after CP init and secure-mode exit, no aperture-related misprogramming across BR/BV/DDE pipes, interrupt recovery for CP faults and hang detect, LLCC activation, accurate GMU timestamp/busy counters, and stress under multi-ring preemption and sysprof.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_gpu.c

## Purpose
`a5xx_gpu.c` is the main Adreno 5xx runtime backend. It handles ring submission and preemption integration, PM4/PFP firmware BO loading, secure ZAP shader handoff, hardware initialization, interrupts and fault diagnosis, suspend/resume, crashdump-backed state capture, speed-bin setup, MMU fault handling, and function dispatch.

## Important APIs, Types, And Functions
The exported table is `a5xx_gpu_funcs`, and the externally used helpers are `a5xx_flush`, `a5xx_idle`, and `a5xx_set_hwcg`. Major private functions include `a5xx_submit`, `a5xx_submit_in_rb`, `a5xx_me_init`, `a5xx_preempt_start`, `a5xx_ucode_load`, `a5xx_zap_shader_init/resume`, `a5xx_hw_init`, `a5xx_recover`, `a5xx_destroy`, `a5xx_fault_handler`, `a5xx_irq`, `a5xx_pm_resume/suspend`, `a5xx_gpu_state_get`, `a5xx_show`, `a5xx_active_ring`, `a5xx_gpu_busy`, `a5xx_get_rptr`, `check_speed_bin`, and `a5xx_gpu_init`.

## Control Flow
Probe allocates `struct a5xx_gpu`, sets register ranges and leakage defaults, reads speed-bin support, chooses four rings except A510, initializes the common Adreno object, installs the SMMU fault handler, initializes preemption records, copies common UBWC config, and sets the UCHE trap base. Firmware loading creates GPU-addressable PM4/PFP BOs, checks PFP patch level for `CP_WHERE_AM_I`, allocates rptr shadow memory when supported, and disables multi-ring preemption when not.

Hardware init programs VBIF, busy counters, hang masks, perf counters, UCHE trap/write-through/GMEM ranges, queue thresholds, ECO workarounds, HWCG, UBWC highest-bank-bit mode, CP protection ranges, secure-video trust range disable, 64-bit address mode, quirk workarounds, common Adreno init, optional GPMU firmware preparation, PM4/PFP instruction bases, ringbuffer base/control, rptr shadow, preemption hardware state, interrupt mask, ME startup, GPMU/power setup, optional A530 stat event, secure mode exit through ZAP shader or `SECVID_TRUST_CNTL`, and final ring yield.

Submit emits preemption setup packets, IB packets, periodic rptr shadow updates, render-mode reset, fence write via `CACHE_FLUSH_TS | IRQ`, context-switch yield, flush, and preemption trigger. IRQ flow clears safe interrupts first, filters errors if requested, dispatches RBBM/CP/hang/UCHE/GPMU handlers, retires cache-flush fences, and handles CP software preempt completion.

## State And Persistence
`struct a5xx_gpu` owns firmware BOs/IOVAs, GPMU BO/dword count, LM leakage, current/next rings, preemption records, last seqnos, preemption state, rptr shadow BO, and `has_whereami`. Hardware state spans protected mode, secure mode, power domains, HWCG, fault masks, and CP context-switch registers. State capture adds RBBM status and optional HLSQ aperture registers read through a crashdump script.

## Dependencies And Integration Points
The file depends on SCM/ZAP firmware, PM OPP/nvmem speed binning, UBWC config, MSM GEM/VM/MMU APIs, Adreno common helpers, A5xx power and preemption modules, debugfs/devcoredump support, worker recovery, timers, and generated A5xx register definitions. Catalog metadata supplies firmware names, quirks, GMEM, and ZAP/GPMU availability.

## Risks
This file is highly sequencing-sensitive. Firmware patch level controls whether rptr shadows and preemption are safe. Secure-mode exit depends on correct ZAP firmware/device-tree configuration. HWCG and power collapse interact with state capture and PM. `a5xx_submit_in_rb` copies user command buffers into the RB and manually idles/retire, so it is a distinct sudo path. IRQ clearing order must avoid RBBM AHB interrupt storms. Crashdump state capture must not run while stalled on an IOMMU fault.

## Test Signals
Signals include firmware BO creation and naming, `has_whereami` enabling shadow rptr/preemption, successful `a5xx_me_init`, ZAP shader load/resume or expected fallback warning, command fences retiring on cache flush, CP SW preempt interrupts switching rings, RBBM/CP fault logs containing useful addresses, SMMU faults including scratch data, suspend clearing shadows, devfreq busy counter increments, coredump HLSQ registers appearing, and clean teardown of all BOs.

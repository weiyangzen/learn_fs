# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_gpu.c

## Purpose
`a4xx_gpu.c` implements the Adreno 4xx backend. It provides command submission, hardware initialization, hardware clock gating, OCMEM/interconnect setup, power suspend/resume behavior, IRQ handling, state capture, timestamp/busy counters, and function dispatch for A405/A420/A430 GPUs.

## Important APIs, Types, And Functions
The exported table is `a4xx_gpu_funcs`. Major helpers are `a4xx_submit`, `a4xx_enable_hwcg`, `a4xx_me_init`, `a4xx_hw_init`, `a4xx_recover`, `a4xx_destroy`, `a4xx_idle`, `a4xx_irq`, `a4xx_gpu_state_get`, `a4xx_pm_resume`, `a4xx_pm_suspend`, `a4xx_get_timestamp`, `a4xx_gpu_busy`, `a4xx_get_rptr`, and `a4xx_gpu_init`. Register range tables are `a4xx_registers` and `a405_registers`.

## Control Flow
Probe allocates `struct a4xx_gpu`, initializes common Adreno state with one ring, chooses the A405 or general A4xx register dump table, allocates OCMEM, sets a UCHE trap base, obtains `gfx-mem` and optional `ocmem` interconnect paths, and requests maximum bandwidth.

Hardware init writes VBIF tuning per variant, busy/perf/hang-detect registers, GMEM base from OCMEM, CP timestamp counter selection, UCHE trap base, CP debug flags, A430-specific SP register file sleep, hardware clock-gating registers, A420 timing workaround, CP protection ranges, interrupt mask, common Adreno hardware setup, ringbuffer base/control, PM4/PFP firmware uploads, ME enable, and `CP_ME_INIT`. Submit flow is close to A3xx but uses `CP_INDIRECT_BUFFER_PFE` and A4xx write-pointer register, then emits `HLSQ_FLUSH`, idle wait, `CACHE_FLUSH_TS | IRQ`, and ring flush.

## State And Persistence
`struct a4xx_gpu` stores OCMEM metadata. The runtime also persists selected register table, UCHE trap base, ring/fence state, perf counter state, and A430 power-collapse state through PM callbacks. GPU snapshots add `RBBM_STATUS`.

## Dependencies And Integration Points
The file depends on generated A4xx registers, Adreno core helpers, OCMEM helpers, interconnect APIs, ring packet macros, MSM PM/recovery/retire hooks, and catalog-provided `adreno_info`. It integrates with debug/devcoredump through `adreno_show` and state hooks.

## Risks
Clock-gating and power sequences contain hardware errata: A420 HLSQ timing, early A430 SP/TP power-collapse issues, and A405 lacking CCU. Incorrect branching can cause hangs that look like generic CP faults. OCMEM allocation is required here, so cleanup and probe failure paths must stay balanced.

## Test Signals
Signals include successful firmware upload and ME init, command completion via fence writes, A430 suspend/resume toggling `RBBM_POWER_CNTL_IP`, timestamp counter reads increasing, OCMEM GMEM base correctness, protected-register faults reporting address/access, and debug state capture showing `RBBM_STATUS`.

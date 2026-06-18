# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_gpu.c

## Purpose
`a3xx_gpu.c` implements the Adreno 3xx runtime backend for MSM DRM. It initializes A305/A306/A320/A330-class hardware, submits command buffers, loads PM4/PFP firmware, handles IRQ retirement, exposes performance counters and debug state, and manages optional OCMEM-backed GMEM.

## Important APIs, Types, And Functions
The exported function table is `a3xx_gpu_funcs`. Key helpers are `a3xx_submit`, `a3xx_me_init`, `a3xx_hw_init`, `a3xx_recover`, `a3xx_destroy`, `a3xx_idle`, `a3xx_irq`, `a3xx_gpu_state_get`, `a3xx_gpu_busy`, `a3xx_get_rptr`, and `a3xx_gpu_init`. `A3XX_INT0_MASK`, `a3xx_registers`, and `perfcntrs` define interrupt, dump, and devfreq/perf counter behavior.

## Control Flow
`a3xx_gpu_init` allocates `struct a3xx_gpu`, sets perf counters and register table, runs common Adreno initialization with one ring, optionally allocates OCMEM for A330/A305B, obtains `gfx-mem` and optional `ocmem` interconnect paths, and currently raises both to a maximum bandwidth derived from `gpu->fast_rate`.

`a3xx_hw_init` writes variant-specific VBIF tuning for A305, A305B, A306/A306A, A320, A330v2, and A330, then programs busy masks, hysteresis, AHB reporting, power counters, hang detection, UCHE cacheline mode, clock gating, OCMEM GMEM base, perf counter selectors, interrupt mask, ringbuffer base/control, CP protected-register ranges, PM4/PFP firmware, CP queue thresholds, ME enable, and finally `CP_ME_INIT`.

Submit flow emits `CP_INDIRECT_BUFFER_PFD` packets for context restore and command buffers, writes the seqno to scratch register 2, sends `HLSQ_FLUSH`, waits for idle, emits `CACHE_FLUSH_TS | IRQ` to the fence address, and flushes the ring. IRQ handling reads and clears `RBBM_INT_0_STATUS` and calls `msm_gpu_retire`.

## State And Persistence
`struct a3xx_gpu` stores optional OCMEM state. The common Adreno state stores firmware, ring, register ranges, and `adreno_info`. Runtime state includes selected perf counters, ring fences, CP scratch seqnos, and OCMEM base. GPU state capture adds `RBBM_STATUS`.

## Dependencies And Integration Points
The file depends on generated A3xx registers, ring packet macros, common Adreno helpers, OCMEM helpers, interconnect APIs, DRM state/debug APIs, and MSM retire/recovery/PM helpers. `a3xx_catalog.c` supplies `.gmem`, firmware names, and revision information that decide most branches.

## Risks
The most fragile area is variant-specific VBIF and clock-gating programming. Incorrect revision helpers or catalog data can select an invalid register sequence. OCMEM allocation and interconnect setup errors abort probe for variants that require them. IRQ decoding is minimal, so unexpected faults may only be visible through raw status and hang recovery.

## Test Signals
Signals include successful probe for each A3xx catalog entry, correct firmware load, no `BUG()` branch in init, OCMEM GMEM base setup on A330/A305B, command fences completing, RBBM busy counter changing with workload, interconnect bandwidth requests succeeding, recovery after soft reset, and no repeated hang-detect or AHB status during GLES workloads.

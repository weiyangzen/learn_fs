# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_catalog.c

## Purpose
`a6xx_catalog.c` is the large static catalog for modern Adreno generations driven by the A6xx-family runtime stack. It describes A6xx, A7xx, and A8xx GPUs, including chip IDs, firmware, GMEM sizes, function tables, quirks, ZAP firmware, speed bins, hardware clock-gating lists, CP protection ranges, GBIF settings, GMU settings, power-up/IFPC register lists, BCM bus votes, pipe-scoped register lists, and preemption record sizes.

## Important APIs, Types, And Functions
The file defines multiple immutable data families: HWCg reglists such as `a612_hwcg`, `a615_hwcg`, `a620_hwcg`, `a630_hwcg`, `a640_hwcg`, `a650_hwcg`, `a660_hwcg`, `a690_hwcg`, `a702_hwcg`, `a730_hwcg`, and `a740_hwcg`; protection lists `a630_protect`, `a650_protect`, `a660_protect`, `a690_protect`, `a730_protect`, `x285_protect`, and `a840_protect`; GBIF lists `a640_gbif` and `a840_gbif`; reglist descriptors such as `a7xx_pwrup_reglist`, `a750_ifpc_reglist`, `a7xx_dyn_pwrup_reglist`, `a840_pwrup_reglist`, `a840_ifpc_reglist`, `x285_dyn_pwrup_reglist`, and `a840_dyn_pwrup_reglist`; non-context register lists for A8xx; and catalog arrays `a6xx_gpus`, `a7xx_gpus`, and `a8xx_gpus` exported with `DECLARE_ADRENO_GPULIST`.

## Control Flow
The file has no active runtime algorithm besides compile-time build assertions. At probe time the common catalog machinery matches chip IDs and machine constraints, then stores the selected `struct adreno_info`. A6xx/A7xx/A8xx runtime code consumes nested `struct a6xx_info` pointers to program HWCg, CP protection, GMU CGC mode/chipid, GBIF CX registers, prim FIFO thresholds, IFPC save/restore lists, dynamic pipe register lists, and bus bandwidth channels.

## State And Persistence
All tables are read-only. Their values persist indirectly through `adreno_gpu->info` and nested `a6xx_info`. Because many entries use compound literals for `struct a6xx_info` and BCM arrays, the catalog is the single source for per-SKU hardware policy.

## Dependencies And Integration Points
The file depends on `adreno_gpu.h`, `a6xx_gpu.h`, generated A6xx/A6xx GMU register headers, catalog macros for GPU lists/protection/reglists, and runtime function tables including `a6xx_gpu_funcs`, `a6xx_gmuwrapper_funcs`, `a7xx_gpu_funcs`, and `a8xx_gpu_funcs`. Firmware names cover SQE, GMU, and AQE slots.

## Risks
Catalog correctness is critical and easy to regress. Wrong HWCg/protect lists can cause hangs, security exposure, or inaccessible perf/debug registers. Several entries share chip IDs but distinguish machines or speed bins, so ordering and metadata matter. A7xx/A8xx pipe-scoped lists and IFPC lists must match runtime save/restore expectations. Build assertions only check protection list capacity, not semantic correctness.

## Test Signals
Signals include every listed chip ID probing to the intended function table, firmware requests matching the SKU, speed-bin mapping selecting supported OPPs, HWCg/protect/GBIF lists programming without CP protection faults, IFPC resume restoring listed registers, preemption record allocations matching catalog sizes, BCM votes appearing for SH0/MC0/ACV where declared, and `BUILD_BUG_ON` not firing for protection list counts.

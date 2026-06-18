# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a7xx_perfcntrs.xml

## Purpose
`a7xx_perfcntrs.xml` defines A7xx performance-counter selector enums. It is the larger A7xx counterpart to the A6xx counter catalog, adding selectors for newer front-end, shader, ray tracing, VRS, UFC, GBIF, cache, and mesh/task-style activity while preserving familiar block categories.

## Important definitions
The file imports common Adreno and PM4 definitions, then defines 18 enums with 966 total values. Shared-style blocks include CP, RBBM, PC, VFD, HLSQ, VPC, TSE, RAS, UCHE, TP, SP, RB, VSC, CCU, LRZ, and CMPDECMP. A7xx-specific or expanded blocks include `a7xx_gbif_perfcounter_select` with 81 GBIF/AXI events and `a7xx_ufc_perfcounter_select` with 58 UFC/filter/cache events.

The larger catalogs show A7xx architectural growth: CP includes AQE and mesh/task chunk counters; HLSQ includes SPTROC and per-stage cache miss events; TP grows to 133 selectors including packed-point and richer cache/filter activity; SP grows to 151 selectors including RTU ray-box/ray-triangle intersections and RTU stall cycles; RB includes VRS quad counters; UCHE includes CCHE/GMEM/UBWC traffic; GBIF exposes AXI read/write beat and held-off events.

## Control flow and generation behavior
The file is converted into `generated/a7xx_perfcntrs.xml.h` and included through `a6xx_gpu.h`. Runtime counter programming selects events by writing these values to performance-counter selector registers. The XML controls the symbolic constants for mux values; register addresses and readout mechanics live in the broader Adreno driver.

## State and persistence
The XML itself is immutable source. Generated values become transient counter selections on hardware during profiling sessions. Counter selection may require GMU OOB ownership for perf-counter access in A6xx-family runtime paths, and selections last until the driver changes them, the GPU resets, or power state tears down the programming.

## Dependencies and integration points
It shares imports and generation with other Adreno XML files and is listed in the msm Makefile. The generated header integrates with A7xx-capable performance monitoring and any debugfs/perf/sysprof layer that maps metric names to selector values. It also needs to remain distinct from `a6xx_perfcntrs.xml` because many A7xx values are expanded, reserved, or shifted.

## Risks
The risk profile is silent observability corruption. Misnumbered selectors can make performance analysis, regression triage, and power tuning wrong without affecting normal rendering. Reserved values and expanded A7xx-only counters increase the chance of using a selector unsupported by a specific SKU. Names with stage-specific suffixes, RTU/VRS/AQE terms, and cache/traffic distinctions must stay exact enough for tooling and humans to interpret data correctly.

## Test signals
Build checks include XML validation and header generation. Runtime checks should compare idle/busy deltas for each block, exercise workloads targeted at texture, shader, ray tracing, VRS, render backend, UCHE/UBWC, and GBIF traffic, and verify tool-facing metric names resolve to plausible counters. Cross-generation tests should ensure A6xx and A7xx metric tables do not accidentally share incompatible selector constants.

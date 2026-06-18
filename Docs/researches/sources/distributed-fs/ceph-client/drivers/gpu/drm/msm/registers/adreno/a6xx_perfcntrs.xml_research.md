# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_perfcntrs.xml

## Purpose
`a6xx_perfcntrs.xml` defines A6xx performance-counter selector enums for GPU blocks. These enums become generated constants used when programming counter select registers and when decoding or exposing performance metrics for profiling, debugging, and system profiling.

## Important definitions
The file imports common Adreno and PM4 definitions, then defines 16 selector enums with 543 total values. Blocks include CP, RBBM, PC, VFD/VFDP, HLSQ, VPC, TSE, RAS, UCHE, TP, SP, RB, VSC, CCU, LRZ, and CMPDECMP. Counts range from small fixed catalogs such as `a6xx_vsc_perfcounter_select` with 5 values to larger shader/texture catalogs such as `a6xx_sp_perfcounter_select` with 85 values and `a6xx_tp_perfcounter_select` with 57 values.

The counters cover always-count/busy cycles, stall/starve cycles, preemption timing, PM4/SQE activity, primitive and tessellation activity, vertex fetch stalls, HLSQ waves and latency, VPC allocations, raster tile/block activity, UCHE/VBIF traffic, texture cache requests/misses/latency, shader ALU/EFU/wave occupancy, render backend depth/color/CCU interactions, LRZ activity, and compression/decompression read/write/flag events.

## Control flow and generation behavior
The XML is converted to `generated/a6xx_perfcntrs.xml.h` during the msm build and included through `a6xx_gpu.h`. At runtime, driver sysprof/perf code selects a counter by writing one of these values into the relevant block's select registers, then reads the corresponding counter registers. The XML does not define the counter register addresses; it defines the mux values that make those registers count a specific event.

## State and persistence
There is no state in the XML. The selected values become transient GPU performance-counter state after the driver programs counter select registers. Those selections affect profiling observations until changed, reset, or power-cycled. Bad selector values generally do not persist beyond counter configuration, but they can make profiling data misleading.

## Dependencies and integration points
The generated header is part of the Makefile's generated Adreno header set and is included by `a6xx_gpu.h`. It integrates with GMU/sysprof code paths that may need OOB perfcounter access (`GMU_OOB_PERFCOUNTER_SET`) before touching counters, and with tools or debugfs/perf interfaces that map user-visible metrics to selector values.

## Risks
Performance-counter enums are easy to regress without compile failures because the values are just numbers accepted by hardware muxes. Wrong names or values can silently report a different event, breaking profiling and power/performance analysis. Some counters are block- or generation-specific; using A6xx selectors on A7xx/A8xx without checking compatibility can produce reserved counts or misleading data. Typos in names also matter because external tooling may key off generated symbol names.

## Test signals
Build signals include generated-header creation and compilation. Runtime signals include nonzero and plausible counter deltas for busy counters under load, idle counters near expected baselines, block-specific counters responding to targeted workloads such as texture sampling, shader ALU loops, render backend writes, LRZ/depth tests, and preemption tests. Cross-checks against known-good freedreno/Mesa perf queries and vendor traces are useful.

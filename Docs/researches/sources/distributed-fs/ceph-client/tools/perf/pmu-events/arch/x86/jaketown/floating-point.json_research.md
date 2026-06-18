# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/floating-point.json

## Purpose
This JSON file defines Jake Town floating-point and SIMD assist PMU events for perf. Its 15 entries expose floating-point assists, x87 and SIMD input/output assists, SSE scalar and packed computation events, 256-bit SIMD floating-point operations, and AVX/SSE transition assists. It supports analysis of floating-point throughput, vectorization width, and costly assist or transition behavior.

## Important APIs, Types, And Functions
The file is a static array of core event descriptors. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, and `BriefDescription`. All entries use counters `0,1,2,3`. Event families are `FP_ASSIST`, `FP_COMP_OPS_EXE`, `OTHER_ASSISTS`, and `SIMD_FP_256`. `FP_ASSIST.ANY` uses a counter mask, while other entries are direct event-code and unit-mask aliases.

## Control Flow
There is no in-file control flow. Perf parses the descriptors for Jake Town and programs the core PMU when users request these aliases. The table separates scalar, packed, x87, SSE, AVX transition, and 256-bit SIMD events so higher-level metrics can distinguish legacy floating point, SSE arithmetic, AVX-width work, and assist penalties.

## State And Persistence
Only static metadata and default sample periods are persisted. Runtime assist and operation counts are hardware counter values owned by perf sessions. `CounterMask` changes the semantics of the affected event from a simple count to a thresholded condition, depending on the hardware event definition. No floating-point architectural state is stored here.

## Dependencies And Integration Points
The file integrates with Jake Town perf event generation and with metrics that reference floating-point event names, including top-down or HPC-oriented metrics in `jkt-metrics.json`. It depends on the core PMU supporting the listed event codes and on perf preserving these aliases for user scripts and metric expressions.

## Risks And Edge Cases
Floating-point event names can be misleading if treated as exact FLOP counts; some count operations, uops, assists, or transitions rather than mathematical operations. AVX-to-SSE and SSE-to-AVX assists are workload- and ABI-sensitive. Incorrect unit masks would make scalar, packed, single, and double categories overlap incorrectly. Counter-mask semantics need parser support and clear interpretation in metrics.

## Test Signals
Validation includes JSON syntax checks, `jevents` generation, `perf list` visibility, and ability to open representative assist and computation events. Runtime tests should compare scalar SSE, packed SSE, and 256-bit SIMD aliases using controlled microbenchmarks, and should trigger AVX/SSE transition events with mixed instruction sequences.

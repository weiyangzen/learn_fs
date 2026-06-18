# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/floating-point.json

Purpose: Defines 17 Ivy Town core PMU aliases for floating-point assists, FP computational uops, SIMD move elimination, AVX/SSE transition assists, and 256-bit SIMD arithmetic. These aliases support HPC and topdown compute diagnostics.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Families include `FP_ASSIST`, `FP_COMP_OPS_EXE`, `MOVE_ELIMINATION`, `OTHER_ASSISTS`, and `SIMD_FP_256`. The FP computational aliases distinguish x87, SSE scalar single/double, SSE packed single/double, and AVX-256 packed single/double classes.

Control flow: Perf converts the JSON array into alias metadata. Runtime requests such as `FP_COMP_OPS_EXE.SSE_PACKED_DOUBLE` schedule core PMU counters using event select/unit mask values. Derived metrics in `ivt-metrics.json` combine these aliases to estimate scalar/vector FP fractions, x87 use, GFLOPS, FLOP/cycle, assists, and transition penalties.

State and persistence: Static event metadata only. Runtime counts are hardware PMU state and perf output; PEBS or sampling state is not managed by this file.

Dependencies/integration: Depends on Ivy Town core PMU definitions and perf alias parsing. It integrates tightly with metric expressions such as `tma_fp_scalar`, `tma_fp_vector`, `tma_fp_vector_128b`, `tma_fp_vector_256b`, `tma_info_core_flopc`, and `tma_info_system_gflops`.

Risks: These aliases count uops or assists, not necessarily architectural floating-point instructions, so derived FLOP estimates rely on assumptions about vector width and instruction mix. `FP_ASSIST.ANY` uses a counter mask and cycle-like semantics, while other FP assist aliases are count-like. AVX/SSE transition event descriptions are architecture-specific and can be mistaken for generic AVX penalties. Incorrect alias names break several topdown/HPC metrics.

Test signals: Validate schema and uniqueness, run metric parser tests for all FP-related expressions, and smoke-test `perf stat` on scalar, SSE, AVX, and x87 microbenchmarks. Tests should distinguish count events from `CounterMask`-qualified cycle events.

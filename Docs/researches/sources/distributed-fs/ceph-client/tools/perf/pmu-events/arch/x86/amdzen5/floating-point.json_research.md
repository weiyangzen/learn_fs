# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/floating-point.json

Purpose: Defines 135 Zen 5 floating-point, SIMD, MMX/SSE/AVX integer, packed width/type, and FP dispatch fault events for perf.

Important APIs/types/functions: The JSON objects use `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Major families cover `fp_ret_x87_fp_ops.*`, `fp_ret_sse_avx_ops.*`, `fp_ops_retired_by_width.*`, `fp_ops_retired_by_type.*`, `sse_avx_ops_retired.*`, `fp_pack_ops_retired.*`, `packed_int_op_type.*`, and `fp_disp_faults.*`.

Control flow: Perf parses the event table into named CPU PMU aliases. Users and derived metrics can count retired FLOPs, uops by vector width, integer vector categories, and SSE/AVX dispatch faults; `recommended.json` consumes `fp_disp_faults.sse_avx_all` as `sse_avx_stalls`.

State and persistence: No software state is mutated. The persistent contract is the detailed taxonomy of FP/SIMD event names and their masks, including aggregate `.all` aliases used for broad counting.

Dependencies and integration: Integrates with AMD core PMU encodings, perf list/stat, and any HPC tooling that derives FLOP rates from these aliases. It is adjacent to execution retirement events but separates floating/vector categories for analysis.

Risks: Several aggregate masks overlap with narrower masks, so summing all entries double-counts. Zen 5 lacks several Zen 6 additions such as FP16 scalar/packed names, bfloat move/shuffle/logical refinements, VNNI categories, 512-bit packed families, and non-schedulable queue read stalls. Event spelling differs from Zen 6, making formula sharing risky.

Test signals: Validate JSON generation, `perf list fp_`, FLOP microbenchmarks for x87/scalar/packed FP32/FP64, vector integer instruction tests, and workloads that intentionally trigger SSE/AVX dispatch faults.

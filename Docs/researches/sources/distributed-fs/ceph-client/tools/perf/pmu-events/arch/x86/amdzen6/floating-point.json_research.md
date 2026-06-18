# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/floating-point.json

Purpose: Defines 184 Zen 6 floating-point, SIMD integer, packed-width, 512-bit, dispatch-fault, and FP non-schedulable queue stall events.

Important APIs/types/functions: Uses `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Families include `fp_ret_x87_fp_ops.*`, `fp_ret_sse_avx_ops.*`, `fp_ops_ret_by_width.*`, `fp_ops_ret_by_type.*`, `fp_sse_avx_ops_ret.*`, `fp_pack_ops_ret.*`, `fp_pack_int_ops_ret.*`, `fp_disp_faults.*`, `fp_pack_512b_ops_ret.*`, and `fp_nsq_read_stalls.*`.

Control flow: Perf maps these events into named aliases for FP and vector analysis. Recommended metrics outside this work item can use `fp_disp_faults.sse_avx_all`; users can separately count 128/256/512-bit FP and integer vector operation classes, VNNI, bfloat, FP16, and queue read stalls.

State and persistence: No runtime state. The persistent API is a much broader Zen 6 vector taxonomy than Zen 5, including explicit 512-bit categories and NSQ read-stall causes.

Dependencies and integration: Integrates with execution retirement analysis, HPC FLOP accounting, vector-instruction profiling, and any metrics that depend on dispatch faults or vector width.

Risks: Many masks are aggregates over narrower categories, so summing across `.all` and detailed entries double-counts. Some `fp_ret_sse_avx_ops` FP16 scalar/packed entries share the same mask as other categories and require hardware-doc interpretation. This file is especially sensitive to copy/paste mistakes because of the large matrix of operation type and width names.

Test signals: Validate `perf list fp_`, run FP32/FP64/FP16/bfloat/vector-integer/VNNI microbenchmarks, compare expected width-specific counts, and exercise dispatch fault and NSQ stall paths where hardware support is available.

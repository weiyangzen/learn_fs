# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/floating-point.json

## Purpose

`amdzen3/floating-point.json` defines 22 Zen 3 floating-point and SIMD PMU events. It covers FPU pipe assignment, retired SSE/AVX operation classes, serialized operations, move elimination, and mixed SSE/AVX dispatch faults.

## Important records and schema

Entries use `EventName`, `EventCode`, `UMask`, `BriefDescription`, and often `PublicDescription`.

Important families include:

- `fpu_pipe_assignment.total`, `.total3`, `.total2`, `.total1`, `.total0`: counts FP scheduler pipe assignment at total and per-pipe masks.
- `fp_ret_sse_avx_ops.*`: retired add/sub, multiply, divide/square-root, multiply-add, and all SSE/AVX operations.
- `fp_retired_ser_ops.*`: serializing SSE bottom/top and x87 bottom/top operations.
- `fp_num_mov_elim_scal_op.*`: optimized and non-optimized scalar move elimination by single/double precision.
- `fp_disp_faults.*`: mixed SSE/AVX fault/stall categories including 128-bit, 256-bit, and all.

## Control flow and integration

The file is parsed by perf's PMU event generator into core PMU aliases. `amdzen3/recommended.json` references `fp_disp_faults.sse_avx_all` for the `sse_avx_stalls` event/metric surface. Users can combine the retired operation classes for FP throughput analysis, while the descriptions distinguish operation classes from instruction counts.

## State and persistence

There is no mutable state. The persistent contract is the relationship between event aliases, event code `0x00/0x03/0x04/0x05/0x0b` families, and masks. These aliases are part of perf's user-facing PMU vocabulary.

## Dependencies

Dependencies include AMD Zen 3 FPU event definitions and perf's JSON-to-C PMU generation. Recommended metrics and user workflows depend on stable names such as `fp_disp_faults.sse_avx_all`.

## Risks

Floating-point events are easy to misinterpret as direct FLOP metrics across vector widths and operation types. Renaming operation-class aliases can break external tooling, and changing masks can silently shift from per-class to aggregate counts.

## Test signals

Use JSON validation, PMU generation, and `perf list` alias checks. Metric tests should cover `sse_avx_stalls`. Hardware sanity checks can compare retired FP operation counts under synthetic SSE/AVX add, multiply, and divide loops, and check dispatch-fault behavior with mixed SSE/AVX code.

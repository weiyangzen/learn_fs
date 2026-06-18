# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/floating-point.json

## Purpose

`amdzen4/floating-point.json` defines 136 Zen 4 floating-point, SIMD, x87, packed integer, and width/type-specific retired operation events. It provides a much richer FP/SIMD taxonomy than the Zen 3 file.

## Important records and schema

Entries use `EventName`, `EventCode`, `UMask`, and `BriefDescription`.

Important families include:

- `fp_ret_x87_fp_ops.*`: x87 add/sub, multiply, divide/square-root, and aggregate operations.
- `fp_ret_sse_avx_ops.*`: SSE/AVX operation classes and aggregate counts.
- `fp_ops_retired_by_width.*`: retired FP ops by scalar/packed width categories.
- `fp_ops_retired_by_type.*`: retired FP ops by arithmetic type.
- `sse_avx_ops_retired.*`: SSE/AVX operations retired by packed/scalar and operation classes.
- `fp_pack_ops_retired.*`: packed FP operation categories.
- `packed_int_op_type.*`: packed integer operation classes, including arithmetic/logical/shift/compare-style buckets.
- `fp_retired_ser_ops.*`: serialized FP operation categories.
- `fp_disp_faults.*`: mixed SSE/AVX and width-specific dispatch fault/stall categories.

## Control flow and integration

The file is parsed into core PMU aliases. `amdzen4/recommended.json` references `fp_disp_faults.sse_avx_all` for `sse_avx_stalls`. Other aliases are direct user-facing perf event names for detailed FP/SIMD profiling and can be combined with pipeline metrics from `pipeline.json`.

## State and persistence

There is no mutable state. The persistent contract is the detailed alias taxonomy and the event-code/mask mapping for each operation class. Stable names matter because the aliases encode semantic categories used by scripts and perf users.

## Dependencies

Dependencies include AMD Zen 4 FP/SIMD PMU definitions, perf's JSON event schema, and the recommended metric using `fp_disp_faults.sse_avx_all`.

## Risks

The density and similar names create risk of swapped masks or misleading category names. Operation counts by width/type are not automatically normalized to FLOPs without understanding vector width and operation semantics. Renaming `fp_disp_faults.sse_avx_all` breaks the recommended stall alias.

## Test signals

Validate JSON and generated event tables. Run `perf list` on Zen 4 to check alias exposure. Hardware tests should use targeted scalar, packed, x87, packed integer, and mixed SSE/AVX kernels to verify the intended event groups increment while unrelated categories stay low.

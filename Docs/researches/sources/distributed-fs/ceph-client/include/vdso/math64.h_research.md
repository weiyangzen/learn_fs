<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/math64.h -->
# sources/distributed-fs/ceph-client/include/vdso/math64.h

Purpose: supplies vDSO-safe 64-bit arithmetic helpers used by time conversion code without pulling in broader kernel math helpers.

Important APIs and types: `__iter_div_u64_rem()` performs small iterative division with remainder. `mul_u64_u32_add_u64_shr()` computes `((a * mul) + b) >> shift`, using `unsigned __int128` where available or a split 32-bit fallback. `mul_u32_u32()` is provided in the fallback path.

Control flow: time conversion fast paths multiply cycle deltas by clocksource multipliers, add fractional bases, and shift to nanoseconds using these helpers.

State and persistence: no state; pure arithmetic.

Dependencies and integration points: depends on compiler support for overflow builtins and optional int128 config. It integrates with generic vDSO time calculations.

Risks and test signals: risks include shift edge cases, overflow carry handling, compiler optimizing iterative division into unsupported operations, and architecture int128 config mismatch. Test time conversion against kernel reference over max cycle deltas, overflow-protection configs, and compilers with/without int128.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/math64.h -->

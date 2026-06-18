# sources/distributed-fs/ceph-client/lib/test_ubsan.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_ubsan.c` deliberately triggers undefined-behavior sanitizer checks in kernel context. It covers integer overflows, truncation, invalid shifts, out-of-bounds array access, invalid bool/enum values, and misaligned access. The source was read as a complete 174-line file.

## Important APIs, Types, and Functions

The file defines `test_ubsan_fp`, macro `UBSAN_TEST`, individual trigger functions `test_ubsan_add_overflow`, `test_ubsan_sub_overflow`, `test_ubsan_mul_overflow`, `test_ubsan_negate_overflow`, `test_ubsan_divrem_overflow`, `test_ubsan_truncate_signed`, `test_ubsan_shift_out_of_bounds`, `test_ubsan_out_of_bounds`, `test_ubsan_load_invalid_value`, and `test_ubsan_misaligned_access`, plus arrays `test_ubsan_array` and `skip_ubsan_array`.

## Control Flow

On module load, `test_ubsan_init` iterates `test_ubsan_array` and calls each trigger. Every trigger logs which UBSAN config controls detection and then performs the undefined operation using `volatile` values or `OPTIMIZER_HIDE_VAR` to avoid compile-time elimination. Division by zero is placed in `skip_ubsan_array` because it can oops the module.

## State and Persistence Behavior

The module owns no persistent state. All variables are local to trigger functions. Its primary output is sanitizer diagnostics and kernel log messages.

## Dependencies and Integration Points

Direct includes are init, kernel, and module headers. Integration points are UBSAN instrumentation controlled by `CONFIG_UBSAN_INTEGER_WRAP`, `CONFIG_UBSAN_DIV_ZERO`, `CONFIG_UBSAN_SHIFT`, `CONFIG_UBSAN_BOUNDS`, `CONFIG_UBSAN_BOOL`, `CONFIG_UBSAN_ENUM`, and `CONFIG_UBSAN_ALIGNMENT`.

## Risks and Edge Cases

This module intentionally executes undefined behavior; it should be used only in controlled test kernels. Some cases depend on compiler instrumentation and architecture alignment behavior. The skipped divide-by-zero case documents a known oops risk. Optimizer changes may affect whether a trigger is preserved unless guarded by volatile or optimizer hiding.

## Test Signals

Expected signals are `pr_info` lines naming each UBSAN config and matching UBSAN reports when the relevant config is enabled. Module init returns `0`; absence of a report for a disabled config is expected.

# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_log2.h

## Purpose

`pt_log2.h` provides type-generic helpers for power-of-two arithmetic used throughout Generic PT to avoid expensive or undefined divide/mod operations on large address types.

## Important APIs, Types, and Functions

- `log2_to_int_t`, `log2_to_max_int_t`, `log2_div_t`, `log2_div_eq_t`, `log2_mod_t`, `log2_mod_eq_max_t`, `log2_set_mod_t`, `log2_set_mod_max_t`, and `log2_mul_t`.
- Dispatch macro `_dispatch_sz` for 32-bit vs 64-bit bit operations.
- `fls_t`, `ffs_t`, and `ffz_t` wrappers with 32-bit and 64-bit implementations.
- Compile-time `static_assert` checks for basic arithmetic identities.

## Control Flow

The helpers are inline macros/functions used by range math, page-size selection, descriptor encoding, and tests. They operate on log2-encoded sizes rather than byte counts.

## State and Persistence Behavior

No state is stored. All operations are pure arithmetic.

## Dependencies and Integration Points

It depends on Linux bitops and limits headers and is included by `pt_defs.h`.

## Risks and Edge Cases

- Several helpers are undefined for zero inputs or shifts equal to the type width; higher-level full-VA wrappers handle those cases where needed.
- Macro arguments may be evaluated in expression contexts, so callers should avoid side-effect-heavy arguments.
- Correct type selection matters for 32-bit hosts and 64-bit address formats.

## Test Signals

`test_bitops` and page-size KUnit tests validate the helpers across 32-bit and 64-bit values, random low-bit patterns, and high page-size ranges.

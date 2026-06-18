
# sources/distributed-fs/ceph-client/lib/tests/bitops_kunit.c

## Purpose
`bitops_kunit.c` validates core bit operations and order helpers. It covers individual bit mutation APIs and `get_count_order()`/`get_count_order_long()` boundary behavior.

## Important APIs, types, and functions
The suite uses `DECLARE_BITMAP`, `bitmap_zero()`, `set_bit()`, `clear_bit()`, `change_bit()`, `test_bit()`, `test_and_set_bit()`, `test_and_clear_bit()`, `test_and_change_bit()`, `find_first_bit()`, `get_count_order()`, and `get_count_order_long()`. Parameter fixtures are declared with `KUNIT_ARRAY_PARAM_DESC()`.

## Control flow
Parameterized bit tests run across enum-derived bit positions 4, 7, 11, 31, and 88 in a 256-bit bitmap. Each test mutates one bit, verifies visible state and return values, then confirms the bitmap is empty via `find_first_bit() == BITOPS_LENGTH`. Order tests feed selected counts around powers of two and high-bit boundaries. On 64-bit builds, an additional long-count table exercises values above 32 bits.

## State and persistence
Each test allocates only stack bitmaps and local parameters. No state persists between KUnit cases.

## Dependencies and integration points
It depends on `<linux/bitops.h>`, `<linux/module.h>`, and KUnit. It is built by `CONFIG_BITOPS_KUNIT`.

## Risks and edge cases
The order tables encode architecture expectations, especially for `CONFIG_64BIT`. Any change in helper semantics around zero or high-bit rounding must update these fixtures. The bit mutation tests do not exercise concurrent atomicity; they validate single-threaded API semantics.

## Test signals
KUnit parameter descriptions identify the failing bit position or order value. Pass means mutation APIs return prior state correctly, leave expected bitmap content, and order helpers round counts as expected.

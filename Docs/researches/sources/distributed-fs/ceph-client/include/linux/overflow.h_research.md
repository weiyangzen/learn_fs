<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/overflow.h -->
# sources/distributed-fs/ceph-client/include/linux/overflow.h

## Purpose
This header centralizes integer overflow, bounds, and allocation-size helpers. It provides type min/max helpers, checked arithmetic, intentional wrapping arithmetic, range checks, safe structure/flexible-array size calculations, and stack flexible-array construction helpers.

## Important APIs, types, and functions
Core helpers include `type_min()`, `type_max()`, `check_add_overflow()`, `check_sub_overflow()`, `check_mul_overflow()`, `check_shl_overflow()`, `wrapping_add/sub/mul()`, `wrapping_assign_add/sub()`, `overflows_type()`, `range_overflows()`, `range_end_overflows()`, typed variants, `castable_to_type()`, `size_mul()`, `size_add()`, `size_sub()`, `array_size()`, `array3_size()`, `flex_array_size()`, `struct_size()`, `struct_size_t()`, `struct_offset()`, `DEFINE_RAW_FLEX()`, `DEFINE_FLEX()`, `STACK_FLEX_ARRAY_SIZE()`, `typeof_flex_counter()`, `overflows_flex_counter_type()`, and `__set_flex_counter()`.

## Control flow
Checked arithmetic delegates to compiler overflow builtins and forces `__must_check` via `__must_check_overflow()`. Wrapping helpers intentionally use overflow builtins to avoid wrap sanitizers. Constant expressions use `__builtin_choose_expr()` paths so compile-time calculations remain constant when possible; runtime paths use checked arithmetic. Size helpers saturate at `SIZE_MAX`, enabling allocator callers to detect impossible sizes. Flexible-array stack helpers build a union with byte storage sized from `struct_size_t()` and optionally initialize `__counted_by` counters.

## State and persistence
No persistent state is stored. The macros affect compile-time diagnostics, generated code, sanitizer behavior, and stack object layout.

## Dependencies and integration points
It depends on compiler helpers, limits, constant-expression detection, array/build-bug helpers, and flexible-array annotations from compiler type support. It integrates broadly with memory allocation, bounds checking, hardened usercopy/FORTIFY patterns, and counted flexible arrays.

## Risks and test signals
Risks include ignoring `__must_check` overflow results, signed/unsigned type surprises, `check_shl_overflow()` with negative or too-large shifts, treating `SIZE_MAX` saturation as a valid allocation size, stack exhaustion from `DEFINE_FLEX()`, and using flexible counter helpers without prior overflow checks. Test compile-time constant folding, signed/unsigned boundary cases, 32-bit and 64-bit builds, UBSAN/integer-wrap sanitizer builds, allocator overflow KUnit tests, flexible-array counted-by cases, and warning enforcement for unchecked results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/overflow.h -->

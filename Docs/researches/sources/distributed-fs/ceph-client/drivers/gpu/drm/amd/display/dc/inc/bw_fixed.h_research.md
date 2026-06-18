# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/bw_fixed.h

## Purpose

`bw_fixed.h` defines the fixed-point numeric type used by legacy DCE bandwidth and watermark calculations. It represents values as signed 64-bit integers with 24 fractional bits and provides arithmetic, conversion, comparison, min/max, floor, and ceil helpers.

## Important APIs, Types, And Functions

`struct bw_fixed` wraps `int64_t value`. Constants and macros include `BW_FIXED_BITS_PER_FRACTIONAL_PART`, `BW_FIXED_GET_INTEGER_PART`, `BW_FIXED_MIN_I32`, and `BW_FIXED_MAX_I32`. Inline helpers include `bw_min2`, `bw_max2`, `bw_min3`, `bw_max3`, `bw_int_to_fixed`, `bw_fixed_to_int`, `fixed31_32_to_bw_fixed`, `bw_add`, `bw_sub`, `bw_div`, `bw_mod`, and comparisons. External helpers include `bw_int_to_fixed_nonconst`, `bw_frc_to_fixed`, `bw_mul`, `bw_floor2`, and `bw_ceil2`.

## Control Flow

The header mostly inlines simple operations. `bw_int_to_fixed` uses `__builtin_constant_p` and `BUILD_BUG_ON` to reject out-of-range constant conversions at compile time; non-constant values go to `bw_int_to_fixed_nonconst`. Division delegates to fraction conversion, and modulo uses `div64_u64_rem`.

## State And Persistence Behavior

There is no persistent state. All operations return new `bw_fixed` values or primitive comparisons. State is carried by callers in DCE calculation structures.

## Dependencies And Integration Points

It is consumed by `dce_calcs.h` and other legacy bandwidth code. It expects kernel integer types, `BUILD_BUG_ON`, and `div64_u64_rem` to be available through surrounding includes. It bridges fixed31.32 values with the legacy 24-fractional-bit format.

## Risks And Edge Cases

Addition and subtraction do not check overflow. Multiplication/division behavior depends on external implementations and divisor validity. `bw_mod` casts a signed result storage pointer to `uint64_t *`, so negative inputs or zero divisors are risky. `bw_fixed_to_int` truncates toward the raw arithmetic shift behavior. Compile-time range checks apply only to constants.

## Test Signals

Unit tests should cover integer/fraction conversion, negative values, constant boundary values, floor/ceil significance, multiply/divide precision, modulo, and comparisons. DCE bandwidth golden tests catch practical regressions in watermark and clock decisions.

# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance.h

This header defines 128-bit helper arithmetic and mean/variance data structures.

128-bit abstraction:
- Uses native `unsigned __int128` in kernel builds when available and not PA-RISC.
- Falls back to `{ hi, lo }` representation otherwise.
- Provides:
  - `u64_to_u128()`
  - `u128_lo()`
  - `u128_hi()`
  - `u128_add()`
  - `u128_sub()`
  - `u128_shl()`
  - `u128_square()`
  - `u64s_to_u128()`
  - external `u128_div()`

Stats structures:
- `struct mean_and_variance`:
  - sample count
  - sum
  - sum of squares
- `struct mean_and_variance_weighted`:
  - shifted weighted mean
  - shifted weighted variance

Helpers:
- `fast_divpow2()` divides signed values by `2^d` rounding toward zero.
- `mean_and_variance_update()` increments count, sum, and 128-bit sum of squares.
- Declarations for unweighted and weighted getters/update.

Important behavior:
- Squaring uses `abs(v)`, so sample square magnitude is tracked without sign.
- `SQRT_U64_MAX` defines maximum integer square-root input scale.

Research notes:
- The header is portable across kernel architectures lacking native 128-bit integer support.
- The closing comment has a spelling typo: `MEAN_AND_VAIRANCE_H_`.

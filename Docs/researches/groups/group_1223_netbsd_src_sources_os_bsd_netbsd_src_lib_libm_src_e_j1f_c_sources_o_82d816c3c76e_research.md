# Group Research: group_1223_netbsd_src_sources_os_bsd_netbsd_src_lib_libm_src_e_j1f_c_sources_o_82d816c3c76e

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_j1f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_j1f.c

This file implements the float IEEE Bessel functions `__ieee754_j1f(float)` and `__ieee754_y1f(float)`.

For `j1f`, it handles NaN/Inf, sign symmetry, tiny inputs via `x/2`, small inputs with rational approximation on `[0,2]`, and larger inputs with sine/cosine asymptotic forms. For `y1f`, it handles zero as `-inf`, negative inputs as NaN, tiny positive inputs as `-2/(pi*x)`, small inputs with rational correction involving `j1f(x)*logf(x)`, and large inputs with asymptotic sine/cosine formulas.

The static helpers `ponef()` and `qonef()` choose coefficient tables by magnitude range and evaluate asymptotic correction rational functions for `x >= 2`. Dependencies include `sinf`, `cosf`, `sqrtf`, `fabsf`, `__ieee754_logf`, and float word access macros from `math_private.h`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_j1f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_jn.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_jn.c

This file implements double-precision order-`n` Bessel functions `__ieee754_jn(int n, double x)` and `__ieee754_yn(int n, double x)`.

`jn` normalizes negative orders using Bessel parity rules, delegates orders 0 and 1 to `j0`/`j1`, uses forward recurrence when `n <= x`, uses a large-`x` asymptotic shortcut above `2**302`, and otherwise computes a continued-fraction estimate followed by backward recurrence and normalization against `j0` or `j1`. Tiny `x` uses the leading Taylor term `(x/2)^n/n!`.

`yn` rejects zero and negative arguments, normalizes negative orders by sign parity, delegates orders 0 and 1, returns zero for infinite positive input, uses a large-`x` asymptotic formula, and otherwise uses forward recurrence from `y0`/`y1`, stopping if `-inf` is reached.

Dependencies include the order-0/order-1 Bessel kernels, `sin`, `cos`, `sqrt`, `fabs`, `__ieee754_log`, and IEEE word inspection macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_jn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_jnf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_jnf.c

This is the float version of `e_jn.c`, implementing `__ieee754_jnf(int n, float x)` and `__ieee754_ynf(int n, float x)`.

`jnf` mirrors the double algorithm with float thresholds: parity normalization for negative orders/arguments, delegation to `j0f`/`j1f`, forward recurrence for `n <= x`, Taylor fallback for tiny `x`, and continued-fraction plus backward recurrence for `n > x`. It scales the backward recurrence when intermediate values become large to avoid spurious overflow.

`ynf` handles NaN, zero, negative, and infinite inputs, then uses forward recurrence from `y0f` and `y1f`, stopping on `-inf`. Dependencies are the float Bessel primitives, `fabsf`, `__ieee754_logf`, and float bit macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_jnf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_lgamma_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_lgamma_r.c

This file implements the reentrant double logarithmic gamma function `__ieee754_lgamma_r(double x, int *signgamp)`.

It uses fdlibm’s domain split: tiny inputs return `-log(|x|)`, negative non-integers use the reflection formula with a local `sin_pi()` reducer, values near 1 and 2 use polynomial/rational approximations, values in `[2,8)` reduce by recurrence, and large values use a Stirling-style expansion. The sign of `Gamma(x)` is stored through `signgamp`.

Special cases include NaN/Inf, zero, negative integers, exact 1 and 2, and very large values. Dependencies include `floor`, `fabs`, `__ieee754_log`, `__kernel_sin`, `__kernel_cos`, and direct double word access.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_lgamma_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammaf_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammaf_r.c

This file is the float implementation of reentrant logarithmic gamma, `__ieee754_lgammaf_r(float x, int *signgamp)`.

It follows the same fdlibm structure as the double version: reflection for negative non-integers via `sin_pif()`, exact singular handling for zero and negative integers, polynomial approximations near the gamma minimum and around `[1,2]`, recurrence for `[2,8)`, and a Stirling expansion for larger finite inputs.

The coefficient tables and thresholds are float-specific. Dependencies include `floorf`, `fabsf`, `__ieee754_logf`, `__kernel_sinf`, `__kernel_cosf`, and float word extraction macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammaf_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammal.c

This file provides the public long-double `lgammal(long double x)` wrapper.

It weak-aliases `lgammal` to `_lgammal`, declares the global `signgam`, and implements `lgammal(x)` by calling `lgammal_r(x, &signgam)`. It contains no approximation logic itself; all computation is delegated to the reentrant long-double implementation selected elsewhere.

Dependencies are `namespace.h`, `math.h`, `math_private.h`, weak alias support, and the external `signgam`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammal_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammal_r.c

This file is the long-double dispatch layer for `lgammal_r(long double, int *)`.

When `__HAVE_LONG_DOUBLE` is defined, it selects the implementation by `LDBL_MANT_DIG`: 64-bit mantissa includes `../ld80/e_lgammal_r.c`, 113-bit mantissa includes `../ld128/e_lgammal_r.c`, and other formats are rejected at compile time. Without long-double support, it falls back to `lgamma_r(double, int *)`.

It weak-aliases `lgammal_r` to `_lgammal_r` and depends on machine floating-point format headers.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammal_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log.c

This file implements `__ieee754_log(double x)`.

The algorithm normalizes `x = 2^k * (1+f)` with `sqrt(2)/2 < 1+f < sqrt(2)`, computes `log(1+f)` using `s = f/(2+f)` and a degree-14 Remez polynomial, then combines the result with split `ln2_hi`/`ln2_lo` for accurate exponent contribution. It has a small-`f` shortcut using a short series.

Special cases implement IEEE behavior for zero, negative input, subnormals, infinities, and NaNs. Dependencies are only `math.h`, `math_private.h`, and double word manipulation macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log10.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log10.c

This file implements `__ieee754_log10(double x)`.

It handles exceptional inputs like `log`, scales subnormals, extracts an exponent `k`, normalizes the mantissa, and computes `log10(x)` as `k*log10(2)` plus `log(normalized_x)/log(10)`. The base-10 constants are split into high and low pieces so exact powers of 10 in the normal range round as intended under round-to-nearest.

Dependencies include `__ieee754_log`, `math_private.h` word macros, and standard floating-point arithmetic.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log10f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log10f.c

This is the float implementation of base-10 logarithm, `__ieee754_log10f(float x)`.

It scales subnormal inputs by `2**25`, handles zero, negative, Inf, and NaN, normalizes the significand, and combines `__ieee754_logf(x) * 1/log(10)` with split `log10(2)` exponent terms. The algorithm is the float analogue of `e_log10.c`.

Dependencies include `__ieee754_logf` and float word access macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log10f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log2.c

This file implements `__ieee754_log2(double x)`.

It reuses the fdlibm natural-log reduction and polynomial approximation, but returns the exponent `k` plus the reduced logarithm divided by `ln2`. Small reduced arguments use a short correction; other inputs use the same `s = f/(2+f)` polynomial split used by `log`.

Special cases cover zero, negative input, subnormals, Inf, and NaN. Dependencies are `math_private.h` bit access and `scalbn`-style exponent handling through direct word manipulation.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log2f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log2f.c

This file implements `__ieee754_log2f(float x)`.

It is the float counterpart of `e_log2.c`: subnormals are scaled, the input is normalized around 1, a polynomial approximates the reduced log, and the result is converted to base 2 by dividing by `ln2` and adding the extracted exponent.

Dependencies are float constants, `GET_FLOAT_WORD`/`SET_FLOAT_WORD`, and standard arithmetic.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_log2f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_logf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_logf.c

This file implements `__ieee754_logf(float x)`.

It follows the fdlibm double `log` method with float thresholds and constants: normalize to `2^k*(1+f)`, use a small-`f` shortcut or the `s=f/(2+f)` polynomial, and combine with split `ln2_hi`/`ln2_lo`. It handles zero, negative input, subnormals, infinities, and NaNs.

Dependencies are `math_private.h` float word macros and the local float coefficient set.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_logf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_pow.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_pow.c

This file implements `__ieee754_pow(double x, double y)`.

The algorithm computes `log2(|x|)` in high/low pieces, multiplies by `y` using split arithmetic, checks overflow/underflow in the resulting exponent, and evaluates `2**z` with polynomial approximation and exponent adjustment. It includes extensive special-case handling for zero exponents, `x == 1`, NaNs, infinities, zero bases, negative bases, integer parity of `y`, square-root shortcut for `y == 0.5`, and huge exponents.

For negative finite bases, it distinguishes non-integer, odd integer, and even integer exponents to decide NaN and result sign. Dependencies include `fabs`, `scalbn`, `__ieee754_sqrt`, and direct IEEE double word operations.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_pow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_powf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_powf.c

This file implements the float version, `__ieee754_powf(float x, float y)`.

It mirrors the double algorithm with float-specific split constants, bit masks, exponent limits, and overflow/underflow thresholds. It determines whether a negative base has an odd or even integer exponent, handles special `y` values and special `x` values up front, computes a split `y*log2(|x|)`, and reconstructs `2**z`.

Dependencies include `fabsf`, `scalbnf`, `__ieee754_sqrtf`, and float word access macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_powf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_powl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_powl.c

This file is the long-double dispatch layer for `powl(long double, long double)`.

When long double is available, it selects `../ld80/e_powl.c` for 64-bit mantissa long double and `../ld128/e_powl.c` for 113-bit mantissa long double, rejecting unsupported formats. Without long-double support, `powl` falls back to double `pow`.

It weak-aliases `powl` to `_powl` and depends on `namespace.h`, `math.h`, and `<machine/float.h>`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_powl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2.c

This file implements double argument reduction `__ieee754_rem_pio2(double x, double *y)` for trigonometric functions.

It returns the integer multiple `n` and stores the remainder `x - n*pi/2` as `y[0] + y[1]`. Small inputs need no reduction, inputs near one `pi/2` use split constants directly, medium inputs use multiplication by `2/pi` and up to three correction rounds, and large inputs are decomposed into base-`2**24` chunks passed to `__kernel_rem_pio2`.

Special Inf/NaN inputs produce NaN remainders. Dependencies include `__kernel_rem_pio2`, `fabs`, and double word extraction.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2f.c

This file implements float argument reduction `__ieee754_rem_pio2f(float x, float *y)`.

It uses float split constants for small and medium ranges, a 396-hex-digit `2/pi` table for large inputs, and delegates large reductions to `__kernel_rem_pio2f`. It stores the remainder in two float parts and returns the quadrant count with sign.

The medium path includes cancellation checks against a table of `n*pi/2` high words and may perform second or third correction iterations. Dependencies include `fabsf`, float bit macros, and the float kernel reducer.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2f.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2f.h

This header defines `__ieee754_rem_pio2fd(float x, double *y)`, a float-input argument reducer that computes the remainder in double precision.

For medium inputs below about `2**28*pi/2`, it rounds `x * 2/pi` to an integer, subtracts a split `pi/2`, and writes one double remainder. Large inputs are scaled and passed as one chunk to the double `__kernel_rem_pio2`.

It supports optional forced inlining via `INLINE_REM_PIO2F`. Dependencies include `<float.h>`, `rnint`, `irint`, `__kernel_rem_pio2`, and float bit macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2f.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2l.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2l.h

This header provides inline long-double argument reduction `__ieee754_rem_pio2l(long double x, long double *y)` for ld128-style formats.

Medium inputs use 113-bit `2/pi` and split `pi/2` constants, with correction rounds up to 316-bit effective accuracy. Large finite inputs are decomposed into five base-`2**24` chunks and reduced by the shared double `__kernel_rem_pio2`, then recombined into a long-double high/low result.

Inf/NaN produces NaN outputs. The implementation depends on `fpmath.h`, `union IEEEl2bits`, `rnintl`, `i64rint`, and the shared kernel reducer.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_remainder.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_remainder.c

This file implements IEEE double `__ieee754_remainder(double x, double p)`.

It returns `x - [x/p]*p`, where the quotient is rounded to nearest with ties to even. It rejects zero divisor, non-finite `x`, and NaN divisor by returning NaN, reduces `x` with `fmod(x, 2p)`, then adjusts around `p/2` to select the nearest-even remainder and restores the original sign of `x`.

Dependencies include `__ieee754_fmod`, `fabs`, and double word manipulation.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_remainder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_remainderf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_remainderf.c

This file implements float `__ieee754_remainderf(float x, float p)`.

It mirrors the double remainder algorithm: invalid cases return NaN, `x` is reduced with `fmodf(x, p+p)`, exact equality returns signed zero, and comparisons against `p/2` choose the nearest remainder with tie behavior. The original sign bit of `x` is restored at the end.

Dependencies are `__ieee754_fmodf`, `fabsf`, and float word macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_remainderf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_remainderl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_remainderl.c

This file implements public `remainderl(long double x, long double y)` as a thin wrapper around `remquol`.

It declares a local `int quo`, calls `remquol(x, y, &quo)` when long double exists, and falls back to double `remquo` otherwise. It contains no independent reduction algorithm.

Dependencies are `<math.h>` and availability of `remquol` or `remquo`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_remainderl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_scalb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_scalb.c

This file implements legacy double `__ieee754_scalb`.

With `_SCALB_INT`, it directly delegates to `scalbn(x, fn)`. Otherwise, the exponent argument is a double: NaNs propagate, infinite exponents produce multiply/divide behavior, non-integral exponents produce NaN, large exponents are clamped to `+/-65000`, and finite integral exponents call `scalbn`.

The file exists for legacy test-suite compatibility; comments recommend `scalbn` instead. Dependencies include `isnan`, `finite`, `rint`, and `scalbn`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_scalb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_scalbf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_scalbf.c

This file implements the float legacy scaling function `__ieee754_scalbf`.

It mirrors `e_scalb.c`: `_SCALB_INT` builds delegate to `scalbnf`; otherwise NaNs propagate, infinite exponent arguments produce multiply/divide behavior, non-integral exponent arguments return NaN, large exponents clamp to `+/-65000`, and finite integral exponents call `scalbnf`.

Dependencies include `isnanf`, `finitef`, `rintf`, and `scalbnf`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_scalbf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sinh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sinh.c

This file implements double `__ieee754_sinh(double x)`.

It handles Inf/NaN by returning `x+x`, preserves sign through a half multiplier, returns tiny inputs unchanged while raising inexact as appropriate, uses `expm1(|x|)` for `|x| < 22`, uses `0.5*exp(|x|)` up to `log(maxdouble)`, uses split half-exponent multiplication near overflow, and overflows with `x*shuge` beyond the threshold.

Dependencies include `expm1`, `__ieee754_exp`, `fabs`, and double word macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sinh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sinhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sinhf.c

This file implements float `__ieee754_sinhf(float x)`.

It is the float analogue of `e_sinh.c`: special Inf/NaN handling, tiny-input return, `expm1f` for `|x| < 22`, `0.5*expf(|x|)` for the normal large range, half-exponent multiplication near overflow, and forced overflow for larger inputs.

Dependencies include `expm1f`, `__ieee754_expf`, `fabsf`, and float word extraction.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sinhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sinhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sinhl.c

This file implements long-double `sinhl(long double x)` when long double is supported, with a fallback to double `sinh`.

For supported ld80 and ld128 formats, it includes the corresponding long-double exponential kernel, uses polynomial approximations for `|x| < 1`, uses `k_hexpl()` for `1 <= |x| < 64`, uses `hexpl()` up to the overflow threshold, and otherwise overflows with a huge value. Coefficient sets differ for 64-bit and 113-bit mantissas.

It weak-aliases `sinhl` to `_sinhl` and uses `ENTERI`/`RETURNI` precision-control macros, long-double exponent extraction, and `fabsl`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sinhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrt.c

This file implements correctly rounded software double `__ieee754_sqrt(double x)`.

The main implementation is fdlibm’s portable bit-by-bit integer algorithm. It handles NaN/Inf, signed zero, and negative inputs; normalizes subnormal numbers; adjusts odd exponents; generates the square-root significand one bit at a time across high and low words; then uses floating additions with `one +/- tiny` to infer rounding direction and inexact behavior.

The long comment after the implementation documents alternative Newton and reciprocal-root algorithms. Dependencies are double word extraction/insertion macros and no hardware sqrt requirement.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrtf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrtf.c

This file implements correctly rounded software float `__ieee754_sqrtf(float x)`.

It is the float analogue of the double bit-by-bit square-root algorithm: handles Inf/NaN, signed zero, and negative inputs; normalizes subnormals; adjusts exponent parity; builds the root bit by bit; and uses `one +/- tiny` to choose final rounding and raise inexact when needed.

Dependencies are `GET_FLOAT_WORD`/`SET_FLOAT_WORD` and basic integer arithmetic.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrtf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrtl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrtl.c

This file implements long-double `__ieee754_sqrtl(long double x)` when long double exists.

With floating-environment support, it handles NaN/Inf, signed zero, and negative inputs, normalizes subnormals, reduces the exponent, obtains a double `sqrt` estimate, optionally refines for high-precision formats, combines high/low parts, then temporarily switches rounding to toward-zero to perform final correction according to the caller’s rounding mode. Helpers `inc()` and `dec()` move a normal long double by one ulp.

Without fenv support, it falls back to double `__ieee754_sqrt((double)x)`. Dependencies include `<fenv.h>`, `union ieee_ext_u`, machine IEEE layout, and `math_private.h`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrtl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/invtrig.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/invtrig.c

This file is a long-double inverse-trigonometry coefficient dispatch source.

If long double is available, it includes either `../ld80/invtrig.c` or `../ld128/invtrig.c` depending on `LDBL_MANT_DIG`; unsupported long-double formats are rejected. It contains no public functions or coefficients directly in this wrapper.

Dependencies are `math.h`, `<machine/float.h>`, and the selected ld80/ld128 implementation.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/invtrig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_cos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_cos.c

This file implements the double cosine kernel `__kernel_cos(double x, double y)` for reduced arguments in approximately `[-pi/4, pi/4]`.

It evaluates a degree-14 cosine polynomial in `z = x*x`, incorporates the low-order tail `y` as `-x*y`, and uses a `qx` correction for larger reduced arguments to reduce cancellation in `1 - x*x/2`. Tiny inputs return 1 while triggering inexact when appropriate.

Dependencies are only `math_private.h` word macros and the local coefficient table.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_cos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_cosdf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_cosdf.c

This file implements `__kernel_cosdf(double x)`, a double-evaluated kernel returning float cosine for reduced float arguments.

It uses a short polynomial with double coefficients and returns a float. It is optimized for fast single-precision trig paths that reduce arguments into double precision but need a float result. Optional `INLINE_KERNEL_COSDF` controls whether the function is emitted as static inline.

Dependencies are `math.h`, `math_private.h`, and the local polynomial coefficients.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_cosdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_cosf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_cosf.c

This file implements the float cosine kernel `__kernel_cosf(float x, float y)` for reduced arguments.

It mirrors the double `k_cos.c` structure with float coefficients: tiny inputs return 1, a polynomial approximates cosine, `y` corrects for the low tail of argument reduction, and a `qx` split improves accuracy for larger reduced arguments.

Dependencies are float word macros and local coefficient constants.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_cosf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_cospi.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_cospi.h

This header defines inline `__kernel_cospi(double x)` for small `cos(pi*x)` kernels.

It splits `x` into float high and double low parts, multiplies by split `pi_hi`/`pi_lo`, normalizes the two-part result with `_2sumF`, and calls `__kernel_cos(hi, lo)`. The including file must provide the pi split constants and the ordinary cosine kernel.

This is infrastructure for pi-multiple trigonometric functions after higher-level range reduction.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_cospi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_rem_pio2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_rem_pio2.c

This file implements the shared large-argument reducer `__kernel_rem_pio2(double *x, double *y, int e0, int nx, int prec)`.

It computes the low three bits of `N` and the remainder for `x - N*pi/2` using 24-bit chunks of `2/pi`, avoiding full multiplication by skipping exponent-known integer parts. It builds convolution terms, distills them into 24-bit integer chunks, handles rounding/complementing when the fractional part exceeds one half, recomputes when cancellation loses all needed bits, multiplies by chunked `pi/2`, and compresses the result for single, double, extended, or quad precision.

The file contains the large `ipio2` table and `PIo2` chunk table. It is used by double, float-as-double, and long-double reducers.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_rem_pio2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_rem_pio2f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_rem_pio2f.c

This file implements the float-specific large-argument reducer `__kernel_rem_pio2f(float *x, float *y, int e0, int nx, int prec, const int32_t *ipio2)`.

Unlike the double kernel, input chunks are 8-bit integers in float form and quad precision is not supported. The algorithm is otherwise parallel to `k_rem_pio2.c`: convolve chunks with a caller-supplied `2/pi` table, distill into integer chunks, round/complement, recompute on cancellation, multiply by chunked `pi/2`, and compress into output precision.

Dependencies include `scalbnf`, `floorf`, and caller-provided large `2/pi` data.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_rem_pio2f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sin.c

This file implements the double sine kernel `__kernel_sin(double x, double y, int iy)` for reduced arguments.

It uses an odd polynomial approximation for `sin(x)/x` on `[-pi/4, pi/4]`. If `iy == 0`, it evaluates `sin(x)` directly; otherwise it incorporates the low-order tail `y` from range reduction using a compensated formula for `sin(x+y)`.

Tiny inputs return `x` with inexact behavior. Dependencies are local coefficients and double high-word extraction.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sincos.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sincos.h

This header merges double sine and cosine kernels into inline `__kernel_sincos(double x, double y, int iy, double *sn, double *cs)`.

It shares the reduced argument, computes sine through the `k_sin` polynomial and cosine through the `k_cos` polynomial, and writes both results. This avoids duplicated range-reduction and can evaluate shared powers once.

Dependencies are the local sine/cosine coefficient tables and ordinary double arithmetic.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sincos.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sincosf.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sincosf.h

This header defines inline `__kernel_sincosdf(double x, float *sn, float *cs)`, computing float sine and cosine from a double reduced argument.

It uses the same optimized polynomial sets as `k_sindf.c` and `k_cosdf.c`, sharing `z = x*x` and related powers. It returns both results through float pointers.

It is intended for optimized float `sincos` paths after argument reduction.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sincosf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sincosl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sincosl.h

This header defines inline long-double `__kernel_sincosl(long double x, long double y, int iy, long double *sn, long double *cs)` for reduced arguments.

It has separate coefficient sets for ld80 (`LDBL_MANT_DIG == 64`) and ld128 (`LDBL_MANT_DIG == 113`). The function evaluates sine and cosine polynomials, incorporates the low-order argument tail `y`, and stores both outputs. The ld128 path uses higher-degree sine and cosine terms, with some trailing coefficients stored as double.

Unsupported long-double formats are rejected at compile time.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sincosl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sindf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sindf.c

This file implements `__kernel_sindf(double x)`, a double-evaluated sine kernel returning float.

It evaluates a compact polynomial for `sin(x)` on reduced float argument ranges, with coefficients chosen for float result accuracy. Optional `INLINE_KERNEL_SINDF` controls static-inline emission.

Dependencies are `math.h`, `math_private.h`, and the local double coefficient table.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sindf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sinf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sinf.c

This file implements the float sine kernel `__kernel_sinf(float x, float y, int iy)`.

It mirrors `k_sin.c` with float coefficients and thresholds. It evaluates an odd sine polynomial and either ignores or incorporates the low-order tail `y` depending on `iy`.

Dependencies are float word macros and local float coefficients.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sinf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sinpi.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sinpi.h

This header defines inline `__kernel_sinpi(double x)` for small `sin(pi*x)` kernels.

It splits `x`, multiplies by split `pi_hi`/`pi_lo`, normalizes the product with `_2sumF`, and calls `__kernel_sin(hi, lo, 1)`. The including file supplies pi constants and the ordinary sine kernel.

It is helper infrastructure for half-cycle or pi-multiple trigonometric functions.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_sinpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_standard.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_standard.c

This file implements fdlibm compatibility error handling through `__kernel_standard(double x, double y, int type)`.

It maps numeric error codes to historical libm error behavior for domain, singularity, overflow, underflow, and total-loss cases across functions such as `acos`, `asin`, `atan2`, `hypot`, `exp`, Bessel functions, `lgamma`, `log`, `pow`, `sinh`, `sqrt`, `fmod`, `remainder`, `acosh`, `atanh`, `scalb`, and `log2`. Float variants are represented by type codes offset by 100, and some long-double cases by 200-series codes.

Behavior depends on `_LIB_VERSION`: IEEE, POSIX, SVID, and X/Open-style handling differ in return values, `errno`, `matherr()` dispatch, and optional stderr messages. Dependencies include `math.h`, `math_private.h`, `<errno.h>`, and either `fputs` or `write`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_standard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_tan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_tan.c

This file implements the double tangent kernel `__kernel_tan(double x, double y, int iy)`.

For reduced arguments, it evaluates an odd tangent polynomial. For inputs near `pi/4`, it transforms to `tan(pi/4-y) = (1-tan(y))/(1+tan(y))`. The `iy` parameter selects either tangent (`1`) or `-1/tan` (`-1`), with the reciprocal path using compensated division to reduce error.

Tiny inputs have special handling, including reciprocal behavior for signed zero. Dependencies include split `pio4` constants, local tangent coefficients, and double word macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_tan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_tandf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_tandf.c

This file implements `__kernel_tandf(double x, int iy)`, a double-evaluated tangent kernel returning float.

It uses a compact polynomial for float-result tangent and is arranged for parallel evaluation rather than simple Horner form. `iy == 1` returns tangent; otherwise it returns `-1/tan`.

Optional `INLINE_KERNEL_TANDF` controls static-inline emission. Dependencies are local coefficients and ordinary double arithmetic.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_tandf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_tanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_tanf.c

This file implements the float tangent kernel `__kernel_tanf(float x, float y, int iy)`.

It mirrors the double tangent kernel with float constants: tiny input handling, transformation near `pi/4`, odd polynomial approximation, and either tangent or compensated reciprocal output depending on `iy`.

Dependencies include float word macros, local `pio4`/`pio4lo`, and tangent coefficient tables.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/k_tanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/math_private.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/math_private.h

This private header defines the shared low-level infrastructure used throughout NetBSD libm.

It provides endian-aware unions and macros for extracting and setting float, double, ld80, and ld128 bit fields; strict-assignment helpers for excess precision; x86 precision-control macros; two-sum and three-sum normalization macros; NaN mixing helpers; complex construction helpers; prototypes for IEEE elementary functions and kernel functions; and utility rounding helpers `rnint`, `rnintf`, `rnintl`, `irint`, and `i64rint`.

It also defines fast floor macros for `sinpi`/`cospi`-style functions, `struct Double`, declarations for legacy high/low precision helpers, and prototypes for reduced float and long-double trig kernels. Correctness depends on matching machine IEEE layout headers, `BYTE_ORDER`, `union ieee_ext_u`, and C floating-evaluation behavior.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/math_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/namespace.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/namespace.h

This header remaps many public libm and fenv symbol names to underscored internal names during libm builds.

It covers elementary real functions, complex inverse trig functions, long-double variants, `fenv` functions, `finite`, `remquo`, scaling functions, `sincos`, pi-multiple trig functions, and gamma functions. This allows implementation files to call internal symbols and avoid namespace or interposition issues.

The file is purely preprocessor definitions and contains no executable code.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/namespace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_asinh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_asinh.c

This file implements public double `asinh(double x)`.

It uses the identity `asinh(x) = sign(x)*log(|x| + sqrt(x*x+1))` with range-specific stable forms: tiny inputs return `x`, very large inputs use `log(|x|)+ln2`, medium-large inputs use `log(2|x| + 1/(sqrt(x*x+1)+|x|))`, and smaller normal inputs use `log1p(|x| + x*x/(1+sqrt(1+x*x)))`.

Dependencies include `__ieee754_log`, `__ieee754_sqrt`, `log1p`, `fabs`, and double high-word macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_asinh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_asinhf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_asinhf.c

This file implements public float `asinhf(float x)`.

It mirrors the double `asinh` implementation with float thresholds and constants: tiny return, large `logf(|x|)+ln2`, medium-large stable logarithm, and small-normal `log1pf` form. It preserves the sign at the end.

Dependencies include `__ieee754_logf`, `__ieee754_sqrtf`, `log1pf`, `fabsf`, and float word extraction.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_asinhf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_asinhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_asinhl.c

This file implements public long-double `asinhl(long double x)` when long double is available, with fallback to double `asinh`.

For supported ld80 and ld128 formats, it selects large and tiny exponent thresholds from mantissa precision, handles Inf/NaN, returns tiny inputs unchanged, uses `logl(fabsl(x))+ln2` for large inputs, a stable logarithm for `|x| >= 2`, and `log1pl` for smaller normal inputs. It weak-aliases `asinhl` to `_asinhl`.

Dependencies include `namespace.h`, machine IEEE layout, `math_private.h`, `sqrtl`, `logl`, `log1pl`, and long-double exponent macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_asinhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_atan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_atan.c

This file implements public double `atan(double x)` and aliases for environments without separate long double.

It reduces by sign and magnitude into intervals around `0`, `0.5`, `1`, `1.5`, and infinity, evaluates an odd polynomial in the reduced variable, and adds split high/low arctangent constants for the selected interval. Very large finite values return `+/-pi/2`, NaNs propagate, and tiny values return `x` while raising inexact when appropriate.

Dependencies include `namespace.h`, `math_private.h`, weak/strong alias macros, `fabs`, and double word inspection.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_atan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_atanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_atanf.c

This file implements public float `atanf(float x)`.

It is the float counterpart of `s_atan.c`: reduce to one of several intervals, evaluate the odd polynomial split into even and odd powers, add interval constants, restore sign, return `+/-pi/2` for very large finite inputs, and propagate NaN.

It weak-aliases `atanf` to `_atanf`. Dependencies include `fabsf`, float word extraction, and local float coefficient tables.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_atanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_atanl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_atanl.c

This file implements public long-double `atanl(long double x)` when long double exists.

It includes ld80 or ld128 inverse-trig constants/helpers from `invtrig.h`, inspects exponent and significand bits to classify ranges, reduces to intervals around `0`, `0.5`, `1`, `1.5`, or infinity, evaluates long-double polynomial helpers `T_even()` and `T_odd()`, and adds split `atanhi`/`atanlo` constants. Large finite inputs return signed `pi/2`, NaNs propagate, and tiny inputs return `x`.

Dependencies include `namespace.h`, machine IEEE layout, `math_private.h`, and the selected long-double inverse-trig header.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_atanl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cargl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cargl.c

This file implements long-double complex argument `cargl(long double complex z)`.

The function simply returns `atan2l(cimagl(z), creall(z))`, delegating all quadrant, NaN, infinity, and signed-zero behavior to `atan2l`.

Dependencies are `<complex.h>` and `<math.h>`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cargl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrt.c

This file implements public double `cbrt(double x)`.

It preserves the sign, handles NaN/Inf and zero directly, forms a rough cube-root estimate from the exponent bits, handles subnormals by scaling, refines with a rational approximation to about 23 bits, rounds the estimate upward after chopping, and performs one Newton step to reach double precision with error below about 0.667 ulp. The sign bit is restored before return.

When long double is absent, it aliases `cbrtl` to `cbrt`. Dependencies include `namespace.h`, `math_private.h`, and double word access macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrtf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrtf.c

This file implements public float `cbrtf(float x)`.

It preserves sign, handles NaN/Inf and zero, creates a rough cube-root estimate from float exponent bits, scales subnormals by `2**24`, and refines with the same rational approximation family used in the double version. The float version stops after the 23-bit refinement and restores the sign.

Dependencies are `math_private.h` float word macros and local constants.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrtf.c -->
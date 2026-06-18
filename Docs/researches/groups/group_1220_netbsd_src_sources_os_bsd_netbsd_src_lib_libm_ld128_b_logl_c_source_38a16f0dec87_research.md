# Group Research: group_1220_netbsd_src_sources_os_bsd_netbsd_src_lib_libm_ld128_b_logl_c_source_38a16f0dec87

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/b_logl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/b_logl.c

This file provides the ld128 extended-precision helper `__log__D(long double x)`, returning a two-part `struct Double` approximation of `log(x)`.

It uses a 128-entry table of `log(Fj)` split into `logF_head` and `logF_tail`, plus a short polynomial over a tightly reduced argument. The reduction normalizes `x` with `frexpl`, chooses `F = 1 + j/128`, computes `u = 2f / (2F + f)`, and accumulates `m * log(2)`, table terms, and the polynomial correction.

The important implementation detail is the deliberate split result: `r.a` is rounded to float precision and `r.b` carries the residual. This is used by legacy BSD gamma code needing extra precision without a native wider floating type.

Dependencies include `math_private.h`, `union ieee_ext_u`, `LD80C`, `frexpl`, `ldexpl`, and `ilogbl`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/b_logl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/b_tgammal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/b_tgammal.c

This ld128 file is not a full `tgammal` implementation. It creates an imprecise long-double wrapper around the double-precision `tgamma()`.

The macro `DECLARE_IMPRECISE(tgamma)` defines `imprecise_tgammal(long double v)` and returns `tgamma(v)`, losing precision whenever `long double` has more than 53 mantissa bits. If `LDBL_MANT_DIG > 53`, `WARN_IMPRECISE` emits a linker warning through `__warn_references`.

The public symbol is weak-aliased so a more accurate implementation from another library can override it. This makes the file a compatibility fallback rather than a numerical implementation.

Dependencies are `<float.h>`, `<math.h>`, `__weak_alias`, and `__warn_references`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/b_tgammal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/e_lgammal_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/e_lgammal_r.c

This file implements `lgammal_r(long double x, int *signgamp)` for IEEE quad-style 128-bit long double.

It uses Sun fdlibm structure adapted to ld128. It handles NaN/Inf, zero, tiny inputs, negative integers, and negative non-integers through the reflection formula. The helper `sin_pil()` computes `sin(pi*x)` with octant reduction using 112-bit scaling constants and calls `__kernel_sinl`/`__kernel_cosl`.

For positive values, the implementation splits the domain into small intervals around 1, 2, and the lgamma minimum `tc`, then uses separate polynomial/rational approximations. For `2 <= x < 8`, it reduces by recurrence and adds logs of products. For large `x`, it uses a Stirling-series approximation.

The sign of gamma is reported through `signgamp`; singularities return division by volatile zero to raise the expected floating exception.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/e_lgammal_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/e_powl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/e_powl.c

This file implements `powl(long double x, long double y)` for 128-bit long double.

It follows the fdlibm method: compute `log2(abs(x))` in high/low pieces, multiply by `y` with split arithmetic, then compute `2**z` through polynomial approximation and exponent scaling. It contains extensive special-case handling for zero, infinities, NaNs, `x == +/-1`, integer exponents for negative bases, square roots for `y == 0.5`, overflow, and underflow.

For negative bases it determines whether `y` is an odd integer, even integer, or non-integer. Non-integer powers of negative finite values return NaN; odd integer exponents preserve sign.

The code uses quad word access through `ieee_quad_shape_type`, explicit mantissa masking to split high/low parts, and polynomial coefficient arrays for logarithm and exponential approximations.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/e_powl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/e_rem_pio2l.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/e_rem_pio2l.h

This header implements the inline ld128 argument reducer `__ieee754_rem_pio2l(long double x, long double *y)`.

It returns an integer quadrant count and writes the remainder of `x mod pi/2` as `y[0] + y[1]`. Medium-sized inputs use direct multiplication by a 113-bit `2/pi` approximation and up to three correction rounds using split `pi/2` constants. Large inputs are decomposed into base-2^24 chunks and passed to `__kernel_rem_pio2`.

The ld128 constants are wider than the ld80 version: 113 bits of `2/pi` and three 68-bit pieces of `pi/2`. The large-input path builds a five-element `tx` array and a three-element `ty` result.

Special cases set both output words to NaN for Inf/NaN input.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/e_rem_pio2l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/invtrig.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/invtrig.c

This file defines shared ld128 constants for inverse trigonometric functions.

For `asinl()` and `acosl()`, it provides polynomial numerator coefficients `pS0..pS9` and denominator coefficients `qS1..qS9`. For `atanl()`, it defines high and low table constants for argument-reduction breakpoints plus the `aT[]` odd/even polynomial coefficient table. It also defines `pi_lo`.

The file contains no public functions. It is data backing for inverse trig implementations that include `invtrig.h`.

The ld128 coefficient sets are longer than the ld80 versions to support 113-bit precision.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/invtrig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/invtrig.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/invtrig.h

This header declares and aliases the shared ld128 inverse trig constants, defines precision thresholds, and provides inline polynomial evaluators.

Key thresholds include `ASIN_LINEAR`, `ACOS_CONST`, `ATAN_CONST`, and `ATAN_LINEAR`, all derived from `LDBL_MAX_EXP` for 113-bit precision. `THRESH` represents 0.95 in the long-double mantissa format.

It remaps common names like `pS0`, `atanhi`, and `pi_lo` to internal `_ItL_*` symbols to avoid namespace collisions. Inline helpers `P()`, `Q()`, `T_even()`, and `T_odd()` evaluate the approximation polynomials.

This is shared infrastructure, not a standalone implementation.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/invtrig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_cosl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_cosl.c

This file implements the ld128 cosine kernel `__kernel_cosl(long double x, long double y)` for reduced arguments near zero.

The valid domain is roughly `[-pi/4, pi/4]`. It evaluates a high-degree polynomial in `z = x*x`, using coefficients `C1..C12`, then combines the result as `1 - z/2 + correction - x*y`. The `y` parameter carries the low part of a previously reduced argument.

The comments emphasize that 113-bit precision requires special care around the exact `x^2 / 2` term. The function is used by public trig routines and by pi-multiple trig helpers.

Dependencies are minimal: `math_private.h` and long-double arithmetic.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_cosl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_cospil.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_cospil.h

This header defines inline `__kernel_cospil(long double x)`, a helper for computing `cos(pi*x)` after high-level range reduction.

It splits `x` into a double-precision high part and long-double residual, multiplies both by split `pi_hi`/`pi_lo`, renormalizes with `_2sumF`, and calls `__kernel_cosl(hi, lo)`.

The header expects `pi_hi`, `pi_lo`, `_2sumF`, and `__kernel_cosl` to be available from the including file. It avoids redoing public-level quadrant reduction and focuses only on accurate multiplication by pi for small reduced inputs.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_cospil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_expl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_expl.h

This header provides the ld128 exponential kernel used by `expl`, `expm1l`, `cexpl`, and helper scaling paths.

The central routine `__k_expl()` reduces `x` into `k*ln2 + endpoint[n] + r`, using 128 intervals. It then evaluates `exp(r)` with a polynomial and multiplies by a table entry split into high/low parts. The table stores `2^(i/128)` values as long-double high/low pairs.

It also defines `k_hexpl()` and `hexpl()` for half-scaled exponentials and, when complex support is enabled, `__ldexp_cexpl()` for avoiding overflow in complex exponential by splitting the exponent scale.

The ld128 table is larger and more precise than ld80’s; comments note potential performance tradeoffs on architectures where long-double multiplication is slow.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_expl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_sinl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_sinl.c

This file implements the ld128 sine kernel `__kernel_sinl(long double x, long double y, int iy)`.

It operates on reduced arguments in roughly `[-pi/4, pi/4]`. If `iy == 0`, it evaluates the polynomial for `sin(x)` directly. Otherwise it incorporates `y`, the low part of the reduced argument, to compute `sin(x + y)` accurately.

Coefficients `S1..S12` approximate `sin(x)/x` to ld128 accuracy; the highest terms are stored as double where sufficient.

This kernel is shared by ordinary trig functions, gamma reflection helpers, and `sinpil()`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_sinl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_sinpil.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_sinpil.h

This header defines inline `__kernel_sinpil(long double x)` for small reduced `sin(pi*x)` inputs.

It splits `x`, multiplies by split pi constants, normalizes the high/low product with `_2sumF`, and calls `__kernel_sinl(hi, lo, 1)`. Like `k_cospil.h`, it assumes `pi_hi`, `pi_lo`, `_2sumF`, and the kernel sine function are provided by the includer.

Its role is accurate pi multiplication after the public wrapper has already handled quadrants, integers, infinities, and NaNs.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_sinpil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_tanl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_tanl.c

This file implements the ld128 tangent kernel `__kernel_tanl(long double x, long double y, int iy)`.

It evaluates `tan(x+y)` or its reciprocal form for reduced arguments. For inputs near `pi/4`, it transforms the argument using split `pio4`/`pio4lo` constants to maintain accuracy. The polynomial coefficients `T3..T57` approximate `tan(x)/x`.

The `iy` parameter is converted to the historical interface convention: one path returns tangent, the other returns `-1/tan`. The reciprocal path uses a compensated division sequence instead of a simple reciprocal.

The code notes a likely issue around `-0` sign handling in `osign`, inherited from the original implementation.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/k_tanl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_cexpl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_cexpl.c

This file implements `cexpl(long double complex z)` for ld128.

It handles special cases first: real-only input, purely imaginary input, non-finite imaginary parts, and infinite real parts. For normal values, it computes `exp(x) * (cos(y) + i*sin(y))`.

When `x` is too large for plain `expl(x)` but still within the complex exponential scaling range, it calls `__ldexp_cexpl()` from `k_expl.h` to avoid intermediate overflow. Constants `exp_ovfl` and `cexp_ovfl` define the direct and scaled thresholds.

This ld128 version uses numeric comparisons rather than ld80-style direct exponent/mantissa inspection.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_cexpl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_cospil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_cospil.c

This file implements `cospil(long double x)`, computing `cos(pi*x)`.

It uses split high/low pi constants with 169-bit approximation comments. For `|x| <= 1`, it dispatches to sine or cosine pi kernels based on the quadrant. For larger finite values below `2^112`, it splits off the integer part with `FFLOORL128`, evaluates the fractional part, and flips sign based on integer parity.

For very large finite inputs, the code relies on long-double integer spacing: `|x| >= 2^113` is always an even integer, so the answer is `1`; between `2^112` and `2^113`, it uses `fmodl(ax, 2)` to determine parity. Inf/NaN returns NaN through volatile zero.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_cospil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_erfl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_erfl.c

This file implements `erfl(long double x)` and `erfcl(long double x)`.

It is an ld128 adaptation of Sun fdlibm `erf`/`erfc`, with separate rational approximations by input range. Small values use a power-series style approximation; values around 1 use a correction around `erx`; medium and large values use rational approximations for the logarithmic erfc tail and exponentials.

`erfl()` saturates to `+/-1` for sufficiently large magnitude, using volatile `tiny` to raise or avoid expected exceptions. `erfcl()` handles negative large values returning nearly `2`, positive large values underflowing toward `0`, and NaN/Inf cases explicitly.

The implementation depends on `expl`, bit extraction macros, and many coefficient blocks tuned for ld128 accuracy.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_erfl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_exp2l.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_exp2l.c

This file implements `exp2l(long double x)` for ld128.

The algorithm uses Gal/Bachelis-style accurate tables. It reduces `x` into an integer scale `k`, a table index `i0`, and a small residual `z - eps[i0]`. It looks up `2^(i/128 + eps[i])`, evaluates a degree-10 polynomial for the residual, and scales by `2**k`.

Exceptional paths handle NaN, infinities, overflow for `x >= 16384`, underflow for `x <= -16495`, and tiny `|x|` returning `1 + x`.

The file uses ld128-specific bit tricks with `union ieee_ext_u`, table bits from the low word after adding a large `redux` constant, and separate scaling for subnormal results.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_exp2l.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_expl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_expl.c

This file implements `expl(long double x)` and `expm1l(long double x)` for ld128.

`expl()` filters NaN/Inf, overflow, underflow, and tiny inputs, then delegates range reduction and table-polynomial evaluation to `__k_expl()` from `k_expl.h`. It scales the returned high/low result by `2**k`, with special handling near max exponent and subnormal scaling.

`expm1l()` has a separate near-zero path using carefully chosen polynomial ranges around `[-0.1659, 0.1659]`, avoiding cancellation in `exp(x)-1`. Outside that range it reuses the same interval/table reduction but recombines terms differently for `k == 0`, `k == -1`, small negative `k`, and large positive `k`.

Floating environment macros `ENTERI`, `RETURNI`, and `RETURNF` preserve expected rounding/exception behavior.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_expl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_logl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_logl.c

This file implements ld128 `logl`, `log1pl`, `log10l`, and `log2l`.

The core algorithm decomposes `x` into `X * 2**k`, chooses one of 128 intervals, and evaluates `log(1+d)` where `d` is very small. Tables `T[]` provide reciprocal-like `G`, high log terms, and long-double low terms. Optional table `U[]` provides exact helper values to compute `d` accurately without a manual split.

`k_logl()` can return a high/low struct when `STRUCT_RETURN` is enabled; `log10l()` and `log2l()` use this split result and multiply by split inverse constants for accuracy. `log1pl()` performs a separate `1+x` decomposition to avoid cancellation for small `x`.

Special cases include zero to `-Inf`, negative to NaN, subnormal scaling by `2^113`, and Inf/NaN passthrough.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_logl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_nanl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_nanl.c

This file implements `nanl(const char *s)` for ld128.

It uses `_scan_nan()` to parse the payload string into four 32-bit words, then sets the long-double exponent to all ones and forces the quiet-NaN bit in `extu_frach`.

The representation is built through a union containing `union ieee_ext_u` and a `uint32_t bits[4]` view. It is small but architecture-format-sensitive through `math_private.h`.

Its only public behavior is returning a quiet long-double NaN with an optional payload.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_nanl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_sinpil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_sinpil.c

This file implements `sinpil(long double x)`, computing `sin(pi*x)`.

It handles small `|x|` with direct split-pi multiplication, preserving signed zero. For `|x| < 1`, it dispatches by quadrant to `__kernel_sinpil` or `__kernel_cospil`. For larger finite inputs below `2^112`, it splits integer and fractional parts with `FFLOORL128`, evaluates the fractional quadrant, and flips sign using integer parity.

Inf/NaN returns NaN. For `|x| >= 2^112`, every representable value is an integer, so it returns signed zero.

The function is designed to avoid the range-reduction error that would occur with `sinl(pi*x)` for large or special pi-multiple inputs.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_sinpil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_tanpil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_tanpil.c

This file implements `tanpil(long double x)`, computing `tan(pi*x)`.

A private inline `__kernel_tanpil()` multiplies a reduced fractional input by split pi constants and calls `__kernel_tanl`, switching to reciprocal behavior around one-quarter. The public function handles small inputs, half-integers, finite large values, infinities, and NaNs.

For `|x| < 1`, it returns signed small-angle results, infinities at half-integers, and signs based on input. For larger finite values below `2^112`, it splits integer/fractional parts and uses parity to choose signed zero or signed infinity. Above that threshold, values are integral; between `2^112` and `2^113` it still checks even/odd parity with `fmodl`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld128/s_tanpil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/b_expl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/b_expl.c

This file provides the legacy ld80 helper `__exp__LD(long double x, long double c)`.

It computes `exp(x+c)` where `c` is a small correction term, using argument reduction by `k*ln2`, a rational-style correction polynomial, and `ldexpl()` scaling. It is included by the ld80 `b_tgammal.c` implementation, not exposed as a public function.

Constants are stored through `LD80C` unions for exact 80-bit representation. The function handles NaN, overflow, underflow, and infinities explicitly; finite overflow and underflow are forced with large `ldexpl()` calls.

This is legacy BSD gamma support rather than the main modern `expl()` implementation.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/b_expl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/b_logl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/b_logl.c

This file provides the ld80 helper `__log__LD(long double x)`, returning a `struct LDouble` high/low decomposition of `log(x)`.

The algorithm mirrors the ld128 `b_logl.c`: normalize with `frexpl`, choose `F = 1 + j/128`, compute a small transformed variable `u`, apply a short polynomial, and add split table values for `log(F)` and `log(2)`.

The result is split with `r.a` rounded to float precision and `r.b` containing the residual. It is used by legacy `tgammal` code to keep extra precision during Stirling-style products.

This file depends on the local `struct LDouble` declaration from its includer and on `math_private.h`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/b_logl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/b_tgammal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/b_tgammal.c

This file implements a full ld80 `tgammal(long double x)`.

It includes `b_logl.c` and `b_expl.c` for split-precision log and exp helpers. For `x >= 6`, it uses a Stirling approximation in `large_gam()`. For moderate positive inputs, it reduces via `G(x+1)=xG(x)` into a rational approximation around the gamma minimum. For small positive inputs it uses `smaller_gam()` to avoid cancellation near zero.

Negative non-integers use the reflection formula through `neg_gam()`, calling `sinpil()` or `cospil()` and handling extreme negative values via `lgammal()` and `expl()`. Negative integers return NaN.

The public `tgammal()` handles overflow above `xmax`, reciprocal behavior near zero, non-finite inputs, and signs for reflected values.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/b_tgammal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/e_lgammal_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/e_lgammal_r.c

This file implements `lgammal_r(long double x, int *signgamp)` for 80-bit extended precision.

It has the same overall structure as the ld128 version but uses shorter coefficient sets and ld80 bit extraction. Negative inputs use a local `sin_pil()` helper with 63/61-bit rounding thresholds and `__kernel_sinl`/`__kernel_cosl`.

Positive inputs are split into domains below 2, between 2 and 8, and large values. It uses polynomial approximations around 1, 2, and `tc`, recurrence products for `x < 8`, and Stirling expansion for larger inputs.

The function uses `ENTERI`/`RETURNI` to preserve floating-point environment behavior, unlike the ld128 version which directly returns in many paths.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/e_lgammal_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/e_powl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/e_powl.c

This file implements ld80 `powl(long double x, long double y)` using Stephen Moshier/Cephes-style algorithms.

It includes helper polynomial evaluators `__polevll()` and `__p1evll()`, log tables `A[]`/`B[]`, and exponential polynomial `R[]`. The main path computes `x**y` as `2**(y*log2(x))`, using a table of `2^(-i/32)` and pseudo-extended arithmetic.

Special cases cover zeros, infinities, NaNs, negative bases, integer exponents, and huge positive/negative `y`. For integer `y` and integral `x` with `|y| < 32768`, it uses `powil()` exponentiation by squaring.

The implementation uses file-scope temporaries and is less reentrant in style than newer kernels, but all state is internal to the function execution.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/e_powl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/e_rem_pio2l.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/e_rem_pio2l.h

This header implements inline ld80 `__ieee754_rem_pio2l(long double x, long double *y)`.

Medium-sized inputs use a 64-bit `2/pi` approximation and split `pi/2` constants. On x86, some long-double constants are represented as volatile double high/low pairs because long-double constants are slow or problematic on those targets. Large inputs are decomposed into three base-2^24 chunks and passed to `__kernel_rem_pio2`.

It returns the quadrant count and stores the remainder as two long-double words. Inf/NaN produces NaN remainders.

Compared with ld128, this version has smaller medium-size thresholds, fewer chunks, and lower precision constants appropriate to 64-bit extended precision.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/e_rem_pio2l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/invtrig.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/invtrig.c

This file defines shared ld80 constants for inverse trigonometric functions.

It provides `pS0..pS6` and `qS1..qS5` for asin/acos approximations, `atanhi[]` and `atanlo[]` for atan argument-reduction constants, `aT[]` for atan polynomial terms, and `pi_lo`.

It contains data only, no executable functions. The coefficient arrays are shorter than ld128’s because ld80 has a smaller mantissa.

Consumers include inverse trig source files that include `invtrig.h`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/invtrig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/invtrig.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/invtrig.h

This header declares ld80 inverse trig constants and inline polynomial evaluators.

It defines ld80-specific thresholds: linear asin/atan below `2^-32`, acos constant below `2^-65`, and atan constant above `2^65`. It supports an optional `STRUCT_DECLS` mode where constants are represented as a `LONGDOUBLE` struct instead of native long double.

The inline helpers `P()`, `Q()`, `T_even()`, and `T_odd()` evaluate the approximation polynomials when not in struct declaration mode.

It also remaps public-looking coefficient names to internal `_ItL_*` symbols.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/invtrig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_cosl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_cosl.c

This file implements the ld80 cosine kernel `__kernel_cosl(long double x, long double y)`.

It evaluates `cos(x+y)` for reduced inputs around zero using a polynomial in `x*x`. The leading `x^2/2` term is handled separately for exactness. Coefficients above the first terms are stored as double because that precision is sufficient for ld80.

On x86 targets, the first coefficient is split into volatile double high/low constants to avoid slow or broken long-double constants.

The kernel is used by ordinary trig functions and pi-multiple wrappers.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_cosl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_cospil.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_cospil.h

This header defines inline `__kernel_cospil(long double x)` for ld80 `cos(pi*x)` after public range reduction.

It splits `x` with a float high part, multiplies by split double `pi_hi`/`pi_lo`, normalizes via `_2sumF`, and delegates to `__kernel_cosl`.

The use of float splitting differs from ld128’s double split and matches ld80 precision/performance needs. The includer must provide pi constants and the cosine kernel.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_cospil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_expl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_expl.h

This header provides the ld80 exponential kernel shared by `expl`, `expm1l`, and `cexpl`.

`__k_expl()` reduces input using 128 intervals and split `ln2/128` constants, then evaluates a polynomial for the residual and combines it with a table of `2^(i/128)` stored as double high/low pairs. It returns high/low pieces plus an exponent scale `k`.

It also defines `k_hexpl()`, `hexpl()`, and complex-only `__ldexp_cexpl()`. The complex helper scales the real exponential in two exponent factors to avoid overflow while multiplying by sine/cosine.

Compared with ld128, this table uses double pairs, and the polynomial is shorter.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_expl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_sinl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_sinl.c

This file implements the ld80 sine kernel `__kernel_sinl(long double x, long double y, int iy)`.

It approximates `sin(x+y)` for reduced inputs using a polynomial for `sin(x)/x`. If `iy == 0`, it returns the direct approximation for `sin(x)`; otherwise it incorporates the low argument part `y`.

The first coefficient is split on x86 into volatile double high/low pieces; remaining coefficients are double. The design mirrors the cosine kernel’s emphasis on exact leading terms and efficient double coefficients.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_sinl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_sinpil.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_sinpil.h

This header defines inline `__kernel_sinpil(long double x)` for ld80 `sin(pi*x)`.

It splits `x` into float high and residual parts, multiplies with split pi constants, normalizes with `_2sumF`, and calls `__kernel_sinl(hi, lo, 1)`.

The helper assumes public-level range and quadrant decisions have already happened. Its only responsibility is accurate pi multiplication and kernel sine evaluation for small fractional inputs.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_sinpil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_tanl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_tanl.c

This file implements ld80 `__kernel_tanl(long double x, long double y, int iy)`.

It handles reduced tangent arguments, transforming values near `pi/4` with split constants before evaluating the polynomial. Coefficients are tuned for ld80; on x86 the leading tangent and pi/4 constants are split into volatile double pieces.

The function supports both tangent and reciprocal tangent paths through the historical `iy` interface. The reciprocal path uses compensated arithmetic to compute `-1/(x+r)` more accurately than direct division.

As in ld128, a comment flags that `osign` handling is likely wrong for negative zero.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/k_tanl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_cexpl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_cexpl.c

This file implements ld80 `cexpl(long double complex z)`.

It extracts ld80 words for both real and imaginary components to handle zero, NaN, and infinity cases without relying only on generic predicates. Pure real input returns `expl(x) + I*y`; pure imaginary input returns `cos(y) + I*sin(y)`.

For non-finite imaginary values, it follows complex exponential special-case rules for finite/NaN real, negative infinity real, and positive infinity real. For real parts between direct `expl` overflow and complex overflow, it calls `__ldexp_cexpl()` from `k_expl.h`.

Normal inputs compute `expl(x)` and multiply by `sincosl(y)`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_cexpl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_cospil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_cospil.c

This file implements ld80 `cospil(long double x)`.

It computes `cos(pi*x)` with explicit quadrant handling rather than multiplying by pi and calling `cosl` directly. For `|x| < 1`, it selects sine or cosine kernels based on fractional range. For `1 <= |x| < 2^63`, it uses `FFLOORL80` to split off the integer part, evaluates the fractional part, and flips sign based on integer parity.

For non-finite values it returns NaN. For very large finite values, representability determines parity: `|x| >= 2^64` is always an even integer, while `2^63 <= |x| < 2^64` checks the low mantissa bit.

The file uses ld80-specific bit extraction and `ENTERI`/`RETURNI` environment macros.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/ld80/s_cospil.c -->
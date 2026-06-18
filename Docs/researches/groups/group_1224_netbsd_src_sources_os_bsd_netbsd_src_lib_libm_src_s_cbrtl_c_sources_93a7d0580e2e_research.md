# Group Research: group_1224_netbsd_src_sources_os_bsd_netbsd_src_lib_libm_src_s_cbrtl_c_sources_93a7d0580e2e

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrtl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrtl.c

Implements `cbrtl(long double)` for supported long-double formats. It reduces exponent modulo 3, builds a float/double seed, applies Newton refinement, and rescales by the cube-root exponent factor.

Key behavior: handles zero, subnormal, infinity, and NaN explicitly; uses `ENTERI/RETURNI` for floating-point environment handling; supports `LDBL_MANT_DIG == 64` and `113`.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `math_private.h`, `union ieee_ext_u`, `GET_EXPSIGN`, `SET_EXPSIGN`, and float word macros.

Notable risks: tightly coupled to IEEE extended/quad layout and to careful rounding-away steps before the final Newton iteration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrtl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ceil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ceil.c

Implements double `ceil()` by direct IEEE-754 word manipulation. It masks fractional bits, increments positive nonintegral values as needed, preserves signed zero behavior, and raises inexact through the `huge + x` idiom.

Key behavior: returns infinities/NaNs as `x+x`, leaves already integral values unchanged, and aliases `ceill` to `ceil` when there is no real long double.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, and `INSERT_WORDS`.

Notable risks: assumes IEEE double word layout and relies on volatile-style arithmetic side effects for exception flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ceil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ceilf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ceilf.c

Implements float `ceilf()` using the same bit-twiddling approach as `s_ceil.c`. It computes the unbiased exponent, clears fractional bits, and increments positive nonintegral values before truncation.

Key behavior: returns signed zero or `1.0f` for `|x| < 1` depending on sign and nonzero status; returns `x+x` for infinity/NaN.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: exception behavior depends on `huge + x`; portable only for IEEE float layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ceilf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ceill.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ceill.c

Implements `ceill()` for real long double by manipulating `union ieee_ext_u` exponent and fraction fields. It handles both implicit and explicit integer-bit long-double layouts.

Key behavior: rounds toward positive infinity, preserves signed zero for negative magnitudes below 1, increments positive fractional values across high/low significand words, and raises inexact via `huge + x`.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `LDBL_IMPLICIT_NBIT`, `EXT_FRACHBITS`, and `EXT_FRACLBITS`.

Notable risks: carry handling in `INC_MANH` is layout-sensitive; unsupported long-double formats are not covered.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ceill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_clogl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_clogl.c

Implements complex long-double logarithm `clogl(z)`, returning `log(|z|) + i*atan2(y,x)`. It uses special paths to avoid overflow, underflow, and accuracy loss near `|z| == 1`.

Key behavior: handles NaN/Inf through `logl(hypotl())`; uses `log1pl(ay*ay)/2` when real magnitude is 1; rescales extreme inputs; uses Dekker splitting and two-sum helpers for accurate squared-magnitude computation.

Important dependencies: `<complex.h>`, `fpmath.h`, `math_private.h`, `atan2l`, `hypotl`, `logl`, `log1pl`, `_2sum`, and `_2sumF`.

Notable risks: highly sensitive to long-double precision, exponent thresholds, and compensated summation details.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_clogl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_copysign.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_copysign.c

Implements double `copysign(x, y)` by copying the sign bit from `y` into the high word of `x`.

Key behavior: preserves the magnitude and payload bits of `x`, changing only the sign. Provides long-double aliases when long double is not distinct.

Important dependencies: `math_private.h`, `GET_HIGH_WORD`, and `SET_HIGH_WORD`.

Notable risks: assumes IEEE double sign bit location.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_copysign.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_copysignf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_copysignf.c

Implements float `copysignf(x, y)` by replacing `x`'s sign bit with `y`'s sign bit.

Key behavior: leaves all non-sign bits of `x` unchanged, including NaN payload bits.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: assumes IEEE single-precision encoding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_copysignf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_copysignl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_copysignl.c

Implements `copysignl()` for real long double and IBM double-double long double. Extended formats copy the sign field directly; IBM long double applies `copysign()` to both component doubles.

Key behavior: compiled only when `__HAVE_LONG_DOUBLE` or `__HAVE_IBM_LONGDOUBLE` is set.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `union ieee_ext_u`, `union ldbl_u`, and `copysign()`.

Notable risks: IBM double-double handling assumes both component signs should be synchronized.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_copysignl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cos.c

Implements double `cos()` using kernel cosine/sine functions and `__ieee754_rem_pio2()` argument reduction.

Key behavior: directly calls `__kernel_cos()` for `|x| <= pi/4`, returns NaN for Inf/NaN via `x-x`, and maps quadrants after range reduction.

Important dependencies: `namespace.h`, `math_private.h`, `__kernel_cos`, `__kernel_sin`, and `__ieee754_rem_pio2`.

Notable risks: accuracy depends on shared range-reduction and kernel implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cosf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cosf.c

Implements float `cosf()` with float kernels and float argument reduction.

Key behavior: uses `__kernel_cosf()` for small inputs, returns NaN for Inf/NaN, and dispatches by quadrant to sine or cosine kernels.

Important dependencies: `math_private.h`, `__kernel_cosf`, `__kernel_sinf`, and `__ieee754_rem_pio2f`.

Notable risks: shares the same quadrant and range-reduction sensitivities as `cos()`, but with float thresholds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cosf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cosl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cosl.c

Implements `cosl()` for long double, including the ld80 or ld128 range reducer and kernel source directly according to `LDBL_MANT_DIG`.

Key behavior: returns `1.0` for zero/subnormal inputs, NaN for Inf/NaN, uses a `pi/4` fast path, and dispatches by quadrant after `__ieee754_rem_pio2l()`.

Important dependencies: `../ld80/e_rem_pio2l.h`, `../ld80/k_cosl.c`, `../ld128/e_rem_pio2l.h`, `../ld128/k_cosl.c`, and `math_private.h`.

Notable risks: compile-time inclusion couples this file to the exact selected long-double backend.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cosl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cospi.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cospi.c

Implements double `cospi(x)`, computing `cos(pi*x)` with period-aware reduction in units of `x` rather than multiplying by pi for all cases.

Key behavior: handles small values, half-integers, integer parity, Inf/NaN invalid results, and very large integral inputs. Uses `FFLOOR` for `1 <= |x| < 2^52`.

Important dependencies: `k_cospi.h`, `k_sinpi.h`, `math_private.h`, and `copysign`-style bit handling.

Notable risks: parity recovery for large finite values is subtle; exact half-integer handling is required for zero results.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cospi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cospif.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cospif.c

Implements float `cospif(x)` using float/double kernels for `cos(pi*x)`. It mirrors `s_cospi.c` with float thresholds and `FFLOORF`.

Key behavior: returns 1 for tiny inputs while raising inexact when appropriate, returns 0 at half-integers, tracks integer parity up to `2^24`, and produces invalid NaN for Inf/NaN.

Important dependencies: `k_cosdf.c`, `k_sindf.c`, `math_private.h`, and `M_PI`.

Notable risks: kernel macros multiply by `M_PI`; accuracy differs from pure table-based pi reduction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cospif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cospil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cospil.c

Dispatch wrapper for long-double `cospil()`. It includes the ld80 or ld128 implementation when long double is available, otherwise falls back to double `cospi()`.

Key behavior: sets weak alias `cospil/_cospil`; compile-time selects `../ld80/s_cospil.c` or `../ld128/s_cospil.c`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, and backend long-double sources.

Notable risks: behavior is entirely delegated to the selected backend; fallback loses long-double precision.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_cospil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_erf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_erf.c

Implements double `erf()` and `erfc()` using classic FDLIBM interval-specific rational approximations.

Key behavior: uses separate approximations for small `|x|`, near 1, medium-large erfc asymptotics, and saturation/underflow regions. Handles signed infinities and NaNs, and splits `x*x` via truncated `z` for exponent accuracy.

Important dependencies: `math_private.h`, `fabs`, and `__ieee754_exp`.

Notable risks: coefficients and interval thresholds are precision-critical; tiny constants intentionally force inexact/underflow behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_erf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_erff.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_erff.c

Implements float `erff()` and `erfcf()` as a float conversion of the FDLIBM double algorithms.

Key behavior: uses float coefficient sets for the same approximation intervals as `s_erf.c`; handles Inf/NaN, small inputs, saturation, and erfc underflow.

Important dependencies: `math_private.h`, `fabsf`, and `__ieee754_expf`.

Notable risks: precision and exception behavior depend on carefully rounded float coefficients and truncating `z` with word masks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_erff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_erfl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_erfl.c

Dispatch wrapper for long-double `erfl()` and `erfcl()`. It includes the ld80 or ld128 implementation when supported, otherwise falls back to double `erf()`/`erfc()`.

Key behavior: defines weak aliases and selects backend by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_erfl.c`, and `../ld128/s_erfl.c`.

Notable risks: fallback loses precision; backend implementation owns all numerical behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_erfl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2.c

Implements double `exp2(x)` using Gal/Gal-Bachelis table-driven reduction. It uses a 256-entry table with small epsilon corrections and a degree-5 polynomial.

Key behavior: filters NaN, infinities, overflow, underflow, and tiny inputs; reduces via a `redux` rounding trick; scales by constructing powers of two and handles subnormal results by split scaling.

Important dependencies: `math_private.h`, `ieee_double_shape_type`, and `INSERT_WORDS`.

Notable risks: table values, `redux`, and low-word extraction are tightly tied to IEEE double representation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2f.c

Implements float `exp2f(x)` using a 16-entry table and degree-4 polynomial, mostly evaluated in double precision.

Key behavior: handles exceptional values, overflow/underflow trapping, tiny `1+x` results, reduction through a float `redux` trick, and scaling via a constructed double power of two.

Important dependencies: `math_private.h`, `STRICT_ASSIGN`, `GET_FLOAT_WORD`, and `INSERT_WORDS`.

Notable risks: i386 has special volatile double overflow/underflow handling to force correct exceptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2l.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2l.c

Dispatch wrapper for long-double `exp2l()`. It includes the ld80 or ld128 backend when real long double is available, otherwise returns `exp2(x)`.

Key behavior: weak-aliases `exp2l`; backend chosen by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_exp2l.c`, and `../ld128/s_exp2l.c`.

Notable risks: numerical behavior and exception handling live in the backend; fallback narrows to double.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2l.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_expl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_expl.c

Dispatch wrapper for long-double `expl()` and `expm1l()`. It includes ld80 or ld128 implementations when available, otherwise delegates to double `exp()` and `expm1()`.

Key behavior: defines weak aliases for both functions and selects backend by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_expl.c`, and `../ld128/s_expl.c`.

Notable risks: fallback loses precision; backend code controls overflow, underflow, and argument reduction details.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_expl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_expm1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_expm1.c

Implements double `expm1(x)` with FDLIBM argument reduction and a cancellation-resistant rational approximation for `exp(x)-1`.

Key behavior: handles huge/nonfinite inputs, reduces by `k*ln2`, evaluates a polynomial in the primary interval, and uses multiple scaling cases for accurate reconstruction.

Important dependencies: `math_private.h`, high-word access macros, and split `ln2` constants.

Notable risks: reconstruction branches are delicate; algebraic simplification can break near-zero and large-negative accuracy.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_expm1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_expm1f.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_expm1f.c

Implements float `expm1f(x)` as a float adaptation of `s_expm1.c`.

Key behavior: filters overflow/underflow and nonfinite inputs, reduces by split `ln2`, evaluates the scaled polynomial, and reconstructs using float exponent manipulation.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: thresholds and scaling cases are float-specific; exception behavior relies on `huge` and `tiny`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_expm1f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fabs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fabs.c

Implements double `fabs()` by clearing the sign bit in the high word.

Key behavior: preserves NaN payloads and all magnitude bits. Aliases `fabsl` to `fabs` when long double is absent.

Important dependencies: `math_private.h`, `GET_HIGH_WORD`, and `SET_HIGH_WORD`.

Notable risks: assumes IEEE double bit layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fabsf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fabsf.c

Implements float `fabsf()` by clearing the sign bit.

Key behavior: preserves all non-sign bits, including NaN payload bits.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: assumes IEEE single-precision layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fabsf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fabsl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fabsl.c

Implements `fabsl()` for real long double by clearing the extended-format sign field.

Key behavior: compiled only under `__HAVE_LONG_DOUBLE`; fallback implementation is intentionally disabled because libc may define it.

Important dependencies: `<machine/ieee.h>` and `union ieee_ext_u`.

Notable risks: depends on `ext_sign` field availability.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fabsl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fdim.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fdim.c

Implements `fdim()`, `fdimf()`, and `fdiml()` through a macro template.

Key behavior: returns a NaN operand unchanged if either input is NaN; otherwise returns `x - y` when `x > y`, or `0.0`.

Important dependencies: `<math.h>` and `isnan`.

Notable risks: long-double behavior relies on compiler/library `isnan` support; overflow in `x-y` is intentionally not hidden.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fdim.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_finite.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_finite.c

Implements legacy double `finite()` with branchless exponent-bit testing.

Key behavior: returns 1 for finite double values and 0 for infinities/NaNs.

Important dependencies: `namespace.h`, `math_private.h`, and `GET_HIGH_WORD`.

Notable risks: IEEE double encoding is assumed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_finite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_finitef.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_finitef.c

Implements legacy float `finitef()` with branchless exponent-bit testing.

Key behavior: returns 1 for finite floats and 0 for infinities/NaNs.

Important dependencies: `namespace.h`, `math_private.h`, and `GET_FLOAT_WORD`.

Notable risks: IEEE float encoding is assumed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_finitef.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_floor.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_floor.c

Implements double `floor()` by masking IEEE fractional bits and decrementing negative nonintegral values toward negative infinity.

Key behavior: raises inexact with `huge + x`, preserves signed zero, returns `x+x` for Inf/NaN, and aliases `floorl` when long double is absent.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, and `INSERT_WORDS`.

Notable risks: bit-level exponent/fraction logic is IEEE-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_floor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_floorf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_floorf.c

Implements float `floorf()` with direct bit manipulation.

Key behavior: returns `-1.0f` for negative nonzero `|x| < 1`, positive signed zero for positive `|x| < 1`, increments the stored magnitude for negative fractional values before clearing fraction bits, and propagates Inf/NaN as `x+x`.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: exception behavior depends on the `huge + x` idiom.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_floorf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_floorl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_floorl.c

Implements `floorl()` for real long double by manipulating extended significand words.

Key behavior: handles implicit/explicit integer-bit layouts, returns `-1.0L` for negative fractional magnitudes below 1, increments negative nonintegral significands before masking, and raises inexact via `huge + x`.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `EXT_FRACHBITS`, `LDBL_MANT_DIG`, and `INC_MANH`.

Notable risks: carry handling and masks depend on exact long-double representation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_floorl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fma.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fma.c

Implements software double `fma(x,y,z)` with single-rounding semantics using double-double arithmetic.

Key behavior: handles zeros, infinities, NaNs, and signed-zero cancellation specially; scales operands with `frexp`; temporarily forces round-to-nearest for exact product/sum; restores directed rounding behavior; handles subnormal results with sticky-bit adjustment.

Important dependencies: `fenv.h`, `math_private.h`, `frexp`, `ldexp`, `ilogb`, `nextafter`, `feraiseexcept`, and word64 macros.

Notable risks: depends on FPU precision and rounding-mode control; hardware FMA is preferable where available.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaf.c

Implements software float `fmaf()` by evaluating the multiply-add in double and correcting double-rounding halfway cases.

Key behavior: returns the double result for common cases, NaNs, exact sums, and non-round-to-nearest modes; for halfway inexact cases, recomputes toward zero and adjusts the low word if needed.

Important dependencies: `fenv.h`, `math_private.h`, `EXTRACT_WORDS`, and `SET_LOW_WORD`.

Notable risks: changes rounding mode temporarily and includes a volatile workaround for compiler common-subexpression issues.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmal.c

Implements software long-double `fmal()` using doubled long-double precision arithmetic.

Key behavior: mirrors `s_fma.c`: handles special values, scales operands, uses Dekker splitting, adjusts sticky bits with `nextafterl`, restores original rounding, and handles subnormal output carefully.

Important dependencies: `fenv.h`, `<machine/ieee.h>`, `frexpl`, `ldexpl`, `ilogbl`, `nextafterl`, `copysignl`, and `math_private.h`.

Notable risks: `add_and_denormalize()` returns through `ldexp((double)sum.hi, scale)`, so representation assumptions and precision behavior are especially sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmax.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmax.c

Implements double `fmax()` with explicit NaN and signed-zero handling.

Key behavior: returns the non-NaN operand if exactly one input is NaN; when signs differ, returns positive zero over negative zero; otherwise uses `x > y`.

Important dependencies: `<machine/ieee.h>` and `union ieee_double_u`.

Notable risks: direct union field checks are machine IEEE-layout dependent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaxf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaxf.c

Implements float `fmaxf()` with explicit NaN and signed-zero behavior.

Key behavior: suppresses spurious exceptions by inspecting NaNs before comparison; returns positive zero when comparing `+0` and `-0`.

Important dependencies: `<machine/ieee.h>` and `union ieee_single_u`.

Notable risks: field layout is target-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaxf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaxl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaxl.c

Implements long-double `fmaxl()` with direct extended-format inspection.

Key behavior: clears the explicit integer bit before NaN checks, returns the non-NaN operand, handles signed zero by returning the positive value, then compares normally.

Important dependencies: `<machine/ieee.h>`, `union ieee_ext_u`, and `memset`.

Notable risks: assumes extended-format field names and integer-bit conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaxl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmin.c

Implements double `fmin()` with NaN suppression and signed-zero handling.

Key behavior: returns the non-NaN operand if only one input is NaN; when signs differ, returns negative zero; otherwise uses `x < y`.

Important dependencies: `<machine/ieee.h>` and `union ieee_double_u`.

Notable risks: direct IEEE field access is target-dependent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fmin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fminf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fminf.c

Implements float `fminf()` with explicit NaN and signed-zero behavior.

Key behavior: returns the non-NaN operand without raising comparison exceptions and returns negative zero when comparing opposite-signed zeroes.

Important dependencies: `<machine/ieee.h>` and `union ieee_single_u`.

Notable risks: relies on NetBSD single-precision bitfield layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fminf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fminl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fminl.c

Implements long-double `fminl()` with extended-format NaN and signed-zero handling.

Key behavior: clears the explicit integer bit before NaN checks, returns the non-NaN operand, returns negative zero when signs differ, and otherwise compares normally.

Important dependencies: `<machine/ieee.h>`, `union ieee_ext_u`, and `memset`.

Notable risks: long-double field assumptions are format-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_fminl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_frexp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_frexp.c

Implements double `frexp()`, decomposing `x` into mantissa in `[0.5,1)` and an exponent.

Key behavior: returns zero/Inf/NaN unchanged with exponent 0; scales subnormals by `2^54`; rewrites exponent bits to normalize the mantissa.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, `GET_HIGH_WORD`, and `SET_HIGH_WORD`.

Notable risks: assumes IEEE double exponent layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_frexp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_frexpf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_frexpf.c

Implements float `frexpf()`.

Key behavior: returns zero/Inf/NaN unchanged with exponent 0; scales subnormals by `2^25`; rewrites exponent bits to produce a `[0.5,1)` mantissa.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: assumes IEEE float layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_frexpf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_frexpl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_frexpl.c

Implements long-double `frexpl()` for supported extended formats.

Key behavior: returns zero/subnormal, normal, Inf, and NaN through exponent-field inspection; scales subnormals by `2^514`; sets normal mantissa exponent to bias-1.

Important dependencies: `<machine/ieee.h>`, `union ieee_ext_u`, and `LDBL_MAX_EXP == 0x4000`.

Notable risks: value of `*ex` is left unspecified for Inf/NaN, matching source comments; only supported long-double exponent layout is accepted.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_frexpl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogb.c

Implements double `ilogb()`, returning the unbiased binary exponent as an integer.

Key behavior: raises `FE_INVALID` and returns `FP_ILOGB0` for zero; scans subnormal significands; returns exponent for normal values; raises invalid and returns `FP_ILOGBNAN` or `INT_MAX` for NaN/Inf.

Important dependencies: `fenv.h`, `math_private.h`, `isnan`, and word access macros.

Notable risks: subnormal loops are bit-layout dependent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogbf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogbf.c

Implements float `ilogbf()`.

Key behavior: raises invalid for zero, NaN, and infinity; scans subnormals to compute exponent; returns normal exponent from the float exponent field.

Important dependencies: `fenv.h`, `math_private.h`, `GET_FLOAT_WORD`, and `isnan`.

Notable risks: exception behavior depends on platform fenv availability.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogbf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogbl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogbl.c

Implements long-double `ilogbl()`.

Key behavior: raises invalid for zero, NaN, and infinity; scales subnormals by a format-dependent power to normalize; returns exponent minus extended bias.

Important dependencies: `namespace.h`, `fenv.h`, `<machine/ieee.h>`, `union ieee_ext_u`, and `FROM_UNDERFLOW`.

Notable risks: supports only `LDBL_MANT_DIG == 64` or `113`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogbl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_infinity.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_infinity.c

Defines the legacy `__infinity` byte array for double positive infinity.

Key behavior: chooses byte order at compile time using `BYTE_ORDER`.

Important dependencies: `<sys/types.h>` endian definitions.

Notable risks: only encodes IEEE double infinity bytes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_infinity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_isinf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_isinf.c

Implements double `isinf()` by checking for all-ones exponent and zero fraction.

Key behavior: returns 1 for either sign of infinity and 0 otherwise.

Important dependencies: `math_private.h` and `EXTRACT_WORDS`.

Notable risks: no branchless sign distinction; assumes IEEE double layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_isinf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_isinff.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_isinff.c

Implements float `isinff()` by checking the absolute bit pattern against infinity.

Key behavior: returns 1 for positive or negative infinity and 0 otherwise.

Important dependencies: `math_private.h` and `GET_FLOAT_WORD`.

Notable risks: assumes IEEE single-precision layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_isinff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_isnan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_isnan.c

Implements double `isnan()` with branchless bit tests.

Key behavior: folds low-word nonzero state into the high word, compares absolute representation against infinity, and returns 1 only for NaNs.

Important dependencies: `math_private.h` and `EXTRACT_WORDS`.

Notable risks: relies on unsigned wraparound and IEEE double encoding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_isnan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_isnanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_isnanf.c

Implements float `isnanf()` with branchless absolute-bit comparison.

Key behavior: returns 1 when the absolute representation is greater than infinity.

Important dependencies: `math_private.h` and `GET_FLOAT_WORD`.

Notable risks: relies on IEEE float encoding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_isnanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lib_version.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lib_version.c

Defines and initializes FDLIBM compatibility global `_LIB_VERSION`.

Key behavior: selects `_POSIX_`, `_XOPEN_`, `_SVID_`, or `_IEEE_` at compile time based on mode macros.

Important dependencies: `math.h` and `math_private.h`.

Notable risks: global behavior affects legacy wrapper error handling elsewhere in libm.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lib_version.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llrint.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llrint.c

Macro instantiation wrapper for `llrint(double)`. It defines `stype`, `roundit`, `dtype`, and `fn`, then includes `s_lrint.c`.

Key behavior: uses shared lrint template with `rint()` and `long long` result type.

Important dependencies: `s_lrint.c`, `rint`, and fenv handling in the template.

Notable risks: changes to `s_lrint.c` affect this function.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llrint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llrintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llrintf.c

Macro instantiation wrapper for `llrintf(float)`, using `rintf()` and `long long`.

Key behavior: includes `s_lrint.c` after setting template macros.

Important dependencies: `s_lrint.c`, `rintf`, and fenv APIs.

Notable risks: template-based implementation hides function body in another source file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llrintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llrintl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llrintl.c

Macro instantiation wrapper for `llrintl(long double)` when long double exists; otherwise falls back to `llrint()`.

Key behavior: includes `s_lrint.c` with `rintl()` and `long long` result type.

Important dependencies: `s_lrint.c`, `rintl`, and `llrint`.

Notable risks: fallback narrows long double to double.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llrintl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llround.c

Macro instantiation wrapper for `llround(double)`. It uses `round()` and the shared `s_lround.c` template.

Key behavior: sets `DTYPE_MIN/MAX` to `LLONG_MIN/MAX`.

Important dependencies: `s_lround.c`, `round`, and `<limits.h>` through the template.

Notable risks: out-of-range handling is inherited from the template.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llroundf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llroundf.c

Macro instantiation wrapper for `llroundf(float)`.

Key behavior: uses `roundf()` and returns `long long`, with range constants set to `LLONG_MIN/MAX`.

Important dependencies: `s_lround.c` and `roundf`.

Notable risks: template range assumptions depend on source and destination precision.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llroundf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llroundl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llroundl.c

Macro instantiation wrapper for `llroundl(long double)`.

Key behavior: includes `s_lround.c` with `roundl()` and `long long` output.

Important dependencies: `s_lround.c`, `roundl`, and long-double support from the broader libm.

Notable risks: no fallback guard; assumes `roundl`/long double are available for this build path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_llroundl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_log1p.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_log1p.c

Implements double `log1p(x)` with FDLIBM cancellation-resistant reduction and polynomial approximation.

Key behavior: handles `x < -1`, `x == -1`, Inf, NaN, tiny inputs, and large inputs; computes correction term when `1+x` is rounded; evaluates a polynomial in `s = f/(2+f)`.

Important dependencies: `namespace.h`, `math_private.h`, split `ln2` constants, and high-word manipulation.

Notable risks: exactness relies on split constants and normalization thresholds; this is shared as `log1pl` fallback when no long double exists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_log1p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_log1pf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_log1pf.c

Implements float `log1pf(x)` with the same FDLIBM structure as double `log1p()`.

Key behavior: handles domain errors, `-1`, Inf/NaN, tiny inputs, rounded `1+x` correction, and polynomial reconstruction with split float `ln2`.

Important dependencies: `namespace.h`, `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: coefficient and threshold choices are float-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_log1pf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_logb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_logb.c

Implements legacy double `logb()`, returning the floating-point exponent as a double.

Key behavior: returns `-inf` for zero through division by `fabs(x)`, returns `x*x` for Inf/NaN, returns `-1022` for subnormals, and normal exponent otherwise.

Important dependencies: `math_private.h`, `fabs`, and `EXTRACT_WORDS`.

Notable risks: comment notes `ilogb` is preferred; subnormal behavior returns minimum normal exponent rather than scanning.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_logb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_logbf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_logbf.c

Implements float `logbf()`.

Key behavior: returns `-inf` for zero, propagates Inf/NaN via `x*x`, returns `-126` for subnormals, and normal exponent otherwise.

Important dependencies: `math_private.h`, `fabsf`, and `GET_FLOAT_WORD`.

Notable risks: IEEE float encoding assumed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_logbf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_logbl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_logbl.c

Implements long-double `logbl()`.

Key behavior: returns `-inf` for zero, absolute value for NaN/Inf, scales subnormals to normal range, and returns exponent minus extended bias.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `fabsl`, `union ieee_ext_u`, and `FROM_UNDERFLOW`.

Notable risks: supports only 64- and 113-bit long-double mantissas.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_logbl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_logl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_logl.c

Dispatch wrapper for long-double `logl()`, `log10l()`, `log2l()`, and `log1pl()`.

Key behavior: only builds under `__HAVE_LONG_DOUBLE`; selects ld80 or ld128 backend by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_logl.c`, and `../ld128/s_logl.c`.

Notable risks: all numerical behavior is in the included backend source.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_logl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lrint.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lrint.c

Template implementation for `lrint`-family functions. Default instantiation is `lrint(double)`; other files include it after defining macros.

Key behavior: holds the floating-point environment, rounds with `roundit`, casts to integer type, clears spurious `FE_INEXACT` if `FE_INVALID` occurred, then updates the environment.

Important dependencies: `fenv.h`, `math.h`, and template macros `stype`, `roundit`, `dtype`, `fn`.

Notable risks: correctness favors exception semantics over speed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lrint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lrintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lrintf.c

Macro instantiation wrapper for `lrintf(float)` using the shared `s_lrint.c` template.

Key behavior: sets `roundit` to `rintf` and `dtype` to `long`.

Important dependencies: `s_lrint.c` and `rintf`.

Notable risks: exception behavior is inherited from the template.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lrintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lrintl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lrintl.c

Macro instantiation wrapper for `lrintl(long double)`.

Key behavior: uses `rintl()` and returns `long` through the shared `s_lrint.c` template.

Important dependencies: `s_lrint.c` and `rintl`.

Notable risks: assumes long-double `rintl()` availability.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lrintl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lround.c

Template implementation for `lround`-family functions. Default instantiation is `lround(double)`.

Key behavior: checks range against type limits adjusted by 0.5, rounds away from zero via `roundit`, casts to integer, and raises `FE_INVALID` returning `DTYPE_MAX` when out of range.

Important dependencies: `limits.h`, `fenv.h`, `math.h`, and template macros.

Notable risks: compile-time `INRANGE` logic depends on source/destination precision relationships.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lroundf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lroundf.c

Macro instantiation wrapper for `lroundf(float)`.

Key behavior: uses `roundf()` and returns `long`, with `LONG_MIN/MAX` bounds.

Important dependencies: `s_lround.c` and `roundf`.

Notable risks: all range and exception behavior comes from the template.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lroundf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lroundl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lroundl.c

Macro instantiation wrapper for `lroundl(long double)`.

Key behavior: includes `s_lround.c` with `roundl()` and `long` output.

Important dependencies: `s_lround.c`, `roundl`, and `LONG_MIN/MAX`.

Notable risks: template range logic is sensitive for long double to integer conversions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_lroundl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_matherr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_matherr.c

Defines default legacy `matherr()` hook.

Key behavior: returns 0 for all normal exception records and also returns 0 when `arg1` is NaN.

Important dependencies: `math.h`, `math_private.h`, and `struct exception`.

Notable risks: this is legacy SVID-style behavior and is mostly a compatibility hook.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_matherr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_modf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_modf.c

Implements double `modf()`, splitting a value into fractional and integral parts by bit masking.

Key behavior: returns signed fractional zero for integral inputs, stores signed integral zero for `|x| < 1`, handles Inf/NaN specially, and raises no exceptions intentionally.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, and `INSERT_WORDS`.

Notable risks: IEEE double layout and signed-zero handling are central.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_modf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_modff.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_modff.c

Implements float `modff()` by clearing fractional bits according to exponent.

Key behavior: stores signed zero as integral part for `|x| < 1`, returns signed fractional zero for integral values, and returns `0.0/x` for Inf/NaN fractional part.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: IEEE float bit layout assumed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_modff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_modfl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_modfl.c

Implements long-double `modfl()` by masking high or low significand words.

Key behavior: handles integer part in high significand, low significand, and no-fraction cases; preserves signed zero through a static zero array; returns NaN fractional part unchanged.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `LDBL_MANT_DIG`, `EXT_FRACLBITS`, and `union ieee_ext_u`.

Notable risks: `GETFRAC` and mask widths depend on exact extended-format storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_modfl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nan.c

Implements `nan()` and `nanf()` payload construction and shared `_scan_nan()`.

Key behavior: parses optional `0x`-prefixed hex payload strings, fills payload words according to host endianness, discards high-order overflow bits, and forces quiet-NaN exponent/significand bits.

Important dependencies: `<sys/endian.h>`, `<ctype.h>`, `<stdint.h>`, `math_private.h`, and byte-order macros.

Notable risks: comment notes compatibility limits with C standard and gdtoa `hexnan.c`; payload layout is endian-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nearbyint.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nearbyint.c

Implements `nearbyint()`, `nearbyintf()`, and `nearbyintl()` with a macro template.

Key behavior: saves the floating-point environment, calls the corresponding `rint` function, restores the environment with `fesetenv()`, and therefore avoids raising inexact.

Important dependencies: `fenv.h`, `math.h`, and `rint`/`rintf`/`rintl`.

Notable risks: assumes rounding cannot overflow for supported formats.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nearbyint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafter.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafter.c

Implements double `nextafter(x,y)` by incrementing or decrementing the IEEE representation by one ulp.

Key behavior: returns NaN for NaN operands, returns `y` when equal, creates signed min-subnormal from zero, raises underflow/overflow through arithmetic, and aliases long-double variants when no long double exists.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, and `INSERT_WORDS`.

Notable risks: underflow flag forcing depends on evaluating `x*x` before final word insertion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafterf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafterf.c

Implements float `nextafterf(x,y)` by stepping the 32-bit representation toward `y`.

Key behavior: handles NaNs, equality, signed zero to min-subnormal, overflow, and underflow.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: assumes monotonic ordering properties of IEEE float bit patterns with sign-aware branches.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafterf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafterl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafterl.c

Implements long-double `nextafterl()` and aliases `nexttowardl()` to it.

Key behavior: handles NaNs, equality, signed zero to min-subnormal, one-ulp significand stepping, explicit integer-bit handling, m68k special cases, overflow, and underflow.

Important dependencies: `<machine/ieee.h>`, `union ieee_ext_u`, `LDBL_NBIT`, `mask_nbit_l`, and volatile long-double arithmetic.

Notable risks: architecture-specific integer-bit handling is delicate, especially around subnormals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafterl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nexttoward.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nexttoward.c

Implements double `nexttoward(double x, long double y)` for systems with 15-bit long-double exponents.

Key behavior: checks NaNs across double and long double, returns `(double)y` on equality, steps `x` by one double ulp toward long-double `y`, and raises overflow/underflow via arithmetic.

Important dependencies: `<machine/ieee.h>`, `math_private.h`, and `union ieee_ext_u`.

Notable risks: unsupported when `LDBL_MAX_EXP != 0x4000`; direction comparison mixes double and long double.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nexttoward.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nexttowardf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nexttowardf.c

Implements float `nexttowardf(float x, long double y)`.

Key behavior: supports ports where long double is double by remapping union fields, handles NaNs, equality, zero to signed min-subnormal, one-ulp float stepping, and overflow/underflow.

Important dependencies: `<machine/ieee.h>`, `math_private.h`, and `memset`.

Notable risks: compatibility macros emulate extended fields on no-long-double ports; long-double NaN inspection is representation-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_nexttowardf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_remquo.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_remquo.c

Implements double `remquo()`, computing IEEE remainder and low quotient bits using shift-and-subtract arithmetic.

Key behavior: handles zero divisor, nonfinite inputs, NaNs, equal magnitudes, subnormal normalization, quotient accumulation, nearest-even fixup, signed zero remainder, and signed quotient output.

Important dependencies: `namespace.h`, `math_private.h`, `fabs`, and word extraction/insertion macros.

Notable risks: quotient and remainder logic is hand-coded on significand words; the signed zero and negative zero quotient case are subtle.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_remquo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_remquof.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_remquof.c

Implements float `remquof()` with the same shift-and-subtract structure as double `remquo()`.

Key behavior: filters exceptional inputs, normalizes subnormals, computes quotient bits, performs nearest-even remainder fixup, restores sign, and writes signed quotient bits.

Important dependencies: `namespace.h`, `math_private.h`, `fabsf`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: equal-magnitude path sets `*quo = 1` directly; sign handling differs from the double code in that branch.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_remquof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_remquol.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_remquol.c

Implements long-double `remquol()` using extended significand word subtraction.

Key behavior: handles exceptional values via `nan_mix_op`, normalizes subnormal operands, computes remainder and quotient bits with high/low significand words, applies nearest-even fixup, and restores sign.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `math_private.h`, `fabsl`, `nan_mix_op`, and long-double field macros.

Notable risks: assumes high and low significand parts fit configured integer types and that explicit integer-bit macros match architecture.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_remquol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_rint.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_rint.c

Implements double `rint()` according to current rounding mode using the `2^52` addition trick.

Key behavior: returns integral inputs unchanged, handles small magnitudes with signed-zero fixup, returns `x+x` for Inf/NaN, and raises inexact when rounding nonintegral values.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, `SET_HIGH_WORD`, and `INSERT_WORDS`.

Notable risks: depends on current rounding mode and IEEE double precision.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_rint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_rintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_rintf.c

Implements float `rintf()` using the `2^23` addition trick.

Key behavior: handles small values, integral values, Inf/NaN, and current rounding mode; i386 marks the intermediate as volatile to preserve rounding.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: compiler optimization can break rounding behavior, as noted by the i386 workaround.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_rintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_rintl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_rintl.c

Implements long-double `rintl()` using a large shift addition/subtraction trick.

Key behavior: returns Inf/NaN as `x+x`, leaves already integral values unchanged, rounds using current mode, and fixes signed zero for small magnitudes.

Important dependencies: `<machine/ieee.h>`, `math_private.h`, `GET_EXPSIGN`, and long-double shift constants.

Notable risks: source explicitly requires intermediate results to be evaluated in long-double precision; i386-style excess/insufficient precision can break results.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_rintl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_round.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_round.c

Implements double `round()`, rounding halfway cases away from zero using `floor()`.

Key behavior: returns Inf/NaN unchanged; for positive values floors and increments at `>= 0.5`; for negative values rounds magnitude then restores sign.

Important dependencies: `<math.h>`, `fpclassify`, and `floor`.

Notable risks: simpler than bit-twiddling routines and inherits `floor()` behavior and exceptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_round.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_roundf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_roundf.c

Implements float `roundf()` using `floorf()` and away-from-zero halfway handling.

Key behavior: returns Inf/NaN unchanged; handles positive and negative magnitudes symmetrically.

Important dependencies: `<math.h>`, `fpclassify`, and `floorf`.

Notable risks: inherits `floorf()` edge behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_roundf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_roundl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_roundl.c

Implements long-double `roundl()` using `floorl()` and away-from-zero halfway handling.

Key behavior: returns nonfinite inputs unchanged, rounds positive values with `t - x <= -0.5`, and negative values via `floorl(-x)`.

Important dependencies: `namespace.h`, `<math.h>`, `isfinite`, and `floorl`.

Notable risks: only compiled under `__HAVE_LONG_DOUBLE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_roundl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbn.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbn.c

Implements double `scalbn()`, `scalbln()`, and aliases for `ldexp()` by exponent manipulation.

Key behavior: normalizes subnormals by multiplying by `2^54`, handles zero, NaN, Inf, overflow, underflow, normal results, and subnormal results.

Important dependencies: `namespace.h`, `math_private.h`, `copysign`, and word macros.

Notable risks: large `n` guards avoid integer overflow in exponent arithmetic; LP64 and non-LP64 aliasing differs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbnf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbnf.c

Implements float `scalbnf()`, `scalblnf()`, and `ldexpf()` aliases.

Key behavior: scales subnormals by `2^25`, directly rewrites exponent fields, and handles overflow/underflow with signed huge/tiny products.

Important dependencies: `namespace.h`, `math_private.h`, `copysignf`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: integer overflow guards use broad `n` thresholds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbnf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbnl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbnl.c

Implements long-double `scalbnl()`, `scalblnl()`, and `ldexpl()` aliases.

Key behavior: handles trivial zero/n==0, NaN/Inf, exponent overflow guards, denormal normalization, normal exponent rewrite, subnormal scaling, and signed overflow/underflow results.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `union ieee_ext_u`, `copysignl`, and format-specific underflow scale constants.

Notable risks: exponent-bound arithmetic is format-sensitive and only supports 64- or 113-bit mantissas.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbnl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_signgam.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_signgam.c

Defines the global `int signgam = 0` used by legacy gamma/lgamma APIs.

Key behavior: provides storage for sign reporting.

Important dependencies: `math.h` and `math_private.h`.

Notable risks: global mutable state has the usual thread-safety/ABI implications, though this file only defines it.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_signgam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_significand.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_significand.c

Implements double `significand(x)` for IEEE 754-1985 test compatibility.

Key behavior: computes `scalb(x, -ilogb(x))` through internal `__ieee754_scalb`.

Important dependencies: `math_private.h`, `__ieee754_scalb`, and `ilogb`.

Notable risks: behavior for zero/NaN/Inf follows `ilogb` and `scalb` interactions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_significand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_significandf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_significandf.c

Implements float `significandf(x)`.

Key behavior: computes `__ieee754_scalbf(x, -ilogbf(x))`.

Important dependencies: `math_private.h`, `__ieee754_scalbf`, and `ilogbf`.

Notable risks: same special-value behavior caveats as double `significand()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_significandf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sin.c

Implements double `sin()` using FDLIBM kernel functions and `pi/2` argument reduction.

Key behavior: calls `__kernel_sin()` for `|x| <= pi/4`, returns NaN for Inf/NaN, and dispatches by quadrant after `__ieee754_rem_pio2()`.

Important dependencies: `namespace.h`, `math_private.h`, `__kernel_sin`, `__kernel_cos`, and `__ieee754_rem_pio2`.

Notable risks: accuracy depends on shared kernel and range-reduction code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sincos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sincos.c

Implements double `sincos(x, &sin, &cos)` by combining sine and cosine range reduction.

Key behavior: uses a small-input path that returns `sin=x`, `cos=1` while generating inexact as needed; handles Inf/NaN by setting both outputs to NaN; dispatches quadrant mappings with `__kernel_sincos()`.

Important dependencies: `namespace.h`, `math_private.h`, `k_sincos.h`, and `__ieee754_rem_pio2`.

Notable risks: output pointer order is swapped in odd quadrants; sign fixups are easy to regress.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sincos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sincosf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sincosf.c

Implements float `sincosf()` with optimized small-multiple-of-`pi/2` paths before full argument reduction.

Key behavior: handles `|x| <= pi/4`, direct reductions up to about `9*pi/4`, Inf/NaN, and general reduction through `__ieee754_rem_pio2fd()`.

Important dependencies: `e_rem_pio2f.h`, `k_sincosf.h`, `math_private.h`, and double constants for small multiples of `pi/2`.

Notable risks: multiple direct-reduction branches must preserve quadrant signs exactly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sincosf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sincosl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sincosl.c

Implements long-double `sincosl()` or falls back to double `sincos()` when long double is absent.

Key behavior: uses long-double kernels and ld80/ld128 `rem_pio2l` reduction; handles zero/subnormal as `sin=x`, `cos=1`; sets both outputs to NaN for Inf/NaN; maps quadrants.

Important dependencies: `k_sincosl.h`, `../ld80/e_rem_pio2l.h`, `../ld128/e_rem_pio2l.h`, and `math_private.h`.

Notable risks: backend selection and quadrant sign swapping are precision- and format-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sincosl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinf.c

Implements float `sinf()` using float kernels and argument reduction.

Key behavior: direct kernel path for `|x| <= pi/4`, NaN for Inf/NaN, and quadrant dispatch after `__ieee754_rem_pio2f()`.

Important dependencies: `namespace.h`, `math_private.h`, `__kernel_sinf`, `__kernel_cosf`, and `__ieee754_rem_pio2f`.

Notable risks: threshold and reduction accuracy are float-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinl.c

Implements long-double `sinl()` using ld80 or ld128 kernel and range-reduction sources.

Key behavior: returns `x` for zero/subnormal, NaN for Inf/NaN, uses a `pi/4` fast path, and dispatches by quadrant after `__ieee754_rem_pio2l()`.

Important dependencies: `../ld80/e_rem_pio2l.h`, `../ld80/k_sinl.c`, `../ld128/e_rem_pio2l.h`, `../ld128/k_sinl.c`, and `math_private.h`.

Notable risks: direct inclusion of backend C files means compile-time format selection controls the implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpi.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpi.c

Implements double `sinpi(x)`, computing `sin(pi*x)` with direct period-aware reduction.

Key behavior: preserves signed zero, uses split pi for tiny inputs, evaluates kernels for fractional ranges, strips integer parts with `FFLOOR`, flips sign by integer parity, returns signed zero for large integral values, and invalid NaN for Inf/NaN.

Important dependencies: `k_cospi.h`, `k_sinpi.h`, `math_private.h`, `copysign`, and `FFLOOR`.

Notable risks: tiny-input split-pi path and parity handling are precision-critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpif.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpif.c

Implements float `sinpif(x)` as the float counterpart to `sinpi()`.

Key behavior: preserves signed zero, uses split float pi for tiny values, maps fractional intervals to sine/cosine kernels, reduces integer parts with `FFLOORF`, flips sign by parity, returns signed zero for large integral values, and invalid NaN for Inf/NaN.

Important dependencies: `k_cosdf.c`, `k_sindf.c`, `math_private.h`, `copysignf`, and `FFLOORF`.

Notable risks: kernel wrappers multiply by `M_PI`, and parity is only recoverable below the float integer-precision limit.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpil.c

Dispatch wrapper for long-double `sinpil()`. It includes the ld80 or ld128 backend when supported, otherwise falls back to double `sinpi()`.

Key behavior: weak-aliases `sinpil`; selects backend by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_sinpil.c`, and `../ld128/s_sinpil.c`.

Notable risks: fallback narrows precision; backend code owns exact signed-zero, invalid, and parity behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpil.c -->